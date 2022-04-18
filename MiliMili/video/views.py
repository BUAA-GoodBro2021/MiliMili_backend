from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import *
from user.models import *
from video.models import *


# TODO 请务必保证对于视频都是默认是已经过审或者是没有被投诉过多的视频
#  如果不是,需要告诉前端该视频要整改（用户点赞或者收藏列表不会进行删除）

# 判断该视频是否需要整改
def need_verify(video_id):
    video = Video.objects.get(id=video_id)
    if video.isAudit != 1 or video.need_verify != 0:
        result = {'result': 0, 'message': r"该视频好像出了一点问题哦，待会再来看看叭!"}
        return JsonResponse(result)


# 上传视频
def upload_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        # 获取表单信息(必须有的)
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        zone = request.POST.get('zone', '')
        tag1 = request.POST.get('tag1', '')
        tag2 = request.POST.get('tag2', '')
        tag3 = request.POST.get('tag3', '')
        tag4 = request.POST.get('tag4', '')
        tag5 = request.POST.get('tag5', '')

        if title == '' or description == '' or zone == '':
            result = {'result': 0, 'message': r"视频标题或描述或分区不能为空!", "station_message": list_message(user.id)}
            return JsonResponse(result)

        # 常见对象存储的对象
        bucket = Bucket()
        # 创建一个视频对象
        video = Video.objects.create(title=title, description=description, zone=zone, user_id=user_id, tag1=tag1,
                                     tag2=tag2, tag3=tag3, tag4=tag4, tag5=tag5)
        video_id = video.id
        # 获取用户上传的封面并检验是否符合要求
        avatar = request.FILES.get("avatar", None)
        # 如果有封面，审核封面
        suffix_avatar = ''
        if avatar:
            if avatar.size > 1024 * 1024:
                Video.objects.get(id=video_id).delete()
                result = {'result': 0, 'message': r"图片不能超过1M！", "station_message": list_message(user.id)}
                return JsonResponse(result)
            # 获取文件尾缀并修改名称
            suffix_avatar = '.' + avatar.name.split(".")[-1]
            avatar.name = str(video.id) + suffix_avatar
            # 保存到本地
            video.avatar = avatar
            video.save()

            # 先生成一个随机 Key 保存在桶中进行审核
            key = create_code()
            upload_result = bucket.upload_file("cover", key + suffix_avatar, avatar.name)
            # 上传审核
            if upload_result == -1:
                result = {'result': 0, 'message': r"上传失败！"}
                Video.objects.get(id=video_id).delete()
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
                return JsonResponse(result)

            # 审核
            audit_dic = bucket.image_audit("cover", key + suffix_avatar)
            if audit_dic.get("result") != 0:
                result = {'result': 0, 'message': r"视频封面审核失败！"}
                # 删除审核对象
                bucket.delete_object("cover", key + suffix_avatar)
                # 删除本地对象
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                # 删除创建的视频模型
                Video.objects.get(id=video_id).delete()
                # 站内信
                title = "视频封面审核失败！"
                content = "亲爱的" + user.username + ' 你好呀!\n视频封面好像带有一点' + audit_dic.get("label") + '呢！'
                create_message(user_id, title, content)
                result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
                return JsonResponse(result)

            # 删除审核对象
            bucket.delete_object("cover", key + suffix_avatar)

            # 上传是否成功
            upload_result = bucket.upload_file("cover", str(video_id) + suffix_avatar, avatar.name)
            if upload_result == -1:
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                Video.objects.get(id=video_id).delete()
                result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
                return JsonResponse(result)

            # 上传是否可以获取路径
            url = bucket.query_object("cover", str(video_id) + suffix_avatar)
            if not url:
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                Video.objects.get(id=video_id).delete()
                result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
                return JsonResponse(result)
            # 获取对象存储的桶地址
            video.avatar_url = url
            video.save()
            # 删除本地文件
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))

        # 处理上传视频
        video_upload = request.FILES.get("video", None)
        if not video_upload:
            if video.video_url != '':
                # 删除封面
                bucket.delete_object("cover", int(video_id) + suffix_avatar)
            Video.objects.get(id=video_id).delete()
            result = {'result': 0, 'message': r"请上传视频！", "station_message": list_message(user.id)}
            return JsonResponse(result)
        if video_upload.size > 1024 * 1024 * 100:
            if video.video_url != '':
                # 删除封面
                bucket.delete_object("cover", int(video_id) + suffix_avatar)
            Video.objects.get(id=video_id).delete()
            result = {'result': 0, 'message': r"视频大小不能超过100M！", "station_message": list_message(user.id)}
            return JsonResponse(result)
        # 获取文件尾缀并修改名称
        suffix_video = '.' + video_upload.name.split(".")[-1]
        video_upload.name = str(video.id) + suffix_video
        # 保存到本地
        video.video = video_upload
        video.save()

        # 先上传到对象存储
        # 上传是否成功
        upload_result = bucket.upload_file("video", str(video_id) + suffix_video, video_upload.name)
        if upload_result == -1:
            if video.video_url != '':
                # 删除封面
                bucket.delete_object("cover", int(video_id) + suffix_avatar)
            os.remove(os.path.join(BASE_DIR, "/media/" + video_upload.name))
            Video.objects.get(id=video_id).delete()
            result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
            return JsonResponse(result)
        # 上传是否可以获取路径
        url = bucket.query_object("video", str(video_id) + suffix_video)
        if not url:
            if video.video_url != '':
                # 删除封面
                bucket.delete_object("cover", int(video_id) + suffix_avatar)
            os.remove(os.path.join(BASE_DIR, "/media/" + video_upload.name))
            Video.objects.get(id=video_id).delete()
            result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
            return JsonResponse(result)

        # 获取对象存储的桶地址
        video.video_url = url
        video.save()

        # TODO 这里不要删除本地文件啊，后面生成封面要用
        # 删除本地文件
        # os.remove(os.path.join(BASE_DIR, "/media/" + video_upload.name))

        # 上传审核
        audit_dic = bucket.video_audit_submit("video", str(video_id) + suffix_video)
        if audit_dic.get("result", 0) == -1 or audit_dic.get("result", 0) == 0:
            # 删除数据库记录
            Video.objects.get(id=video_id).delete()
            # 删除封面
            bucket.delete_object("cover", int(video_id) + suffix_avatar)
            # 删除视频
            bucket.delete_object("video", int(video_id) + suffix_video)
            # 删除本地文件
            os.remove(os.path.join(BASE_DIR, "/media/" + video_upload.name))
            result = {'result': 0, 'message': r"上传失败！", "station_message": list_message(user.id)}
            return JsonResponse(result)
        # 上传成功，等待审核
        JobToVideo.objects.create(job_id=audit_dic.get("job_id"), video_id=video_id)
        result = {'result': 1, 'message': r"正在审核中，别着急哦！", "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def del_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        user.del_video()
        # 获取视频主体
        video_id = request.POST.get('video_id', '')
        video = Video.objects.get(id=video_id)

        # 删除对象存储的部分
        bucket = Bucket()
        suffix_avatar = '.' + video.avatar_url.split(".")[-1]
        bucket.delete_object("cover", int(video_id) + suffix_avatar)
        suffix_video = '.' + video.video_url.split(".")[-1]
        bucket.delete_object("video", int(video_id) + suffix_video)

        # 清除点赞(先获取谁点赞了视频的列表，把关系解除，作者收获点赞减少)
        video_list = UserToVideo_like.objects.filter(video_id=video_id)
        del_like_num = len(video_list)
        user.like_num -= del_like_num
        video_list.delete()

        # 清除收藏
        video_list = FavoriteToVideo.objects.filter(video_id=video_id)
        del_collect_num = len(video_list)
        user.collect_num -= del_collect_num
        video_list.delete()
        # 清除本身
        video.delete()
        # 站内信
        title = "视频删除成功！"
        content = "亲爱的" + user.username + '你好呀!\n' \
                                          '视频删除成功了，真的是好可惜呢~'
        create_message(user_id, title, content)

        result = {'result': 1, 'message': r"删除视频成功！", "user": user.to_dic(), "station_message": list_message(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取个人点赞视频列表的id
def get_like_list_simple(user_id):
    return [x.video_id for x in UserToVideo_like.objects.filter(user_id=user_id)]


# 获取个人点赞视频列表的详情(具体信息)
def get_like_list_detail(user_id):
    return [Video.objects.get(id=x).to_dic() for x in get_like_list_simple(user_id)]


# 点赞视频
def like_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        # 获取点赞视频编号 并添加点击记录
        video_id = request.POST.get('video_id', '')

        # 判断该视频是否需要整改
        need_verify(video_id)
        # 判断是否已经点赞过
        if UserToVideo_like.objects.filter(user_id=user_id, video_id=video_id).exists():
            result = {'result': 0, 'message': r"已经点赞过，请不要重复点赞!", "user": user.to_dic(),
                      "station_message": list_message(user_id)}
            return JsonResponse(result)

        UserToVideo_like.objects.create(user_id=user_id, video_id=video_id)
        video = Video.objects.get(id=video_id)
        video.add_like()

        # 获取视频的发布者 其收获的点赞数+1
        upload_user = video.user
        upload_user.add_like()

        # 发送站内信
        title = "视频收获点赞啦！"
        content = "亲爱的" + upload_user.username + ''' 你好呀!\n你发布的视频有收获好朋友的点赞了，不好奇是哪位嘛(有可能ta在默默关注你呢~'''
        create_message(upload_user.id, title, content)

        result = {'result': 1, 'message': r"点赞成功！", "user": user.to_dic(), "like_list": get_like_list_detail(user_id),
                  "station_message": list_message(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 取消点赞
def dislike_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        # 获取取消点赞视频编号 并删除点击记录
        video_id = request.POST.get('video_id', '')
        if not UserToVideo_like.objects.filter(user_id=user_id, video_id=video_id).exists():
            result = {'result': 0, 'message': r"已经取消点赞，不要重复取消！", "user": user.to_dic(),
                      "station_message": list_message(user_id)}
            return JsonResponse(result)
        UserToVideo_like.objects.get(user_id=user_id, video_id=video_id).delete()
        video = Video.objects.get(id=video_id)
        video.del_like()
        # 获取视频的发布者 其收获的点赞数-1
        upload_user = video.user
        upload_user.del_like()

        result = {'result': 1, 'message': r"取消成功！", "user": user.to_dic(), "like_list": get_like_list_detail(user_id),
                  "station_message": list_message(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取自己的点赞列表
def like_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        result = {'result': 1, 'message': r"获取点赞列表成功！", "user": user.to_dic(),
                  "like_list": get_like_list_detail(user_id), "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取自己所有视频的收藏夹id
def get_favorite_list_id(user_id):
    return [x.id for x in Favorite.objects.filter(user_id=user_id)]


# 获取收藏夹内部的视频视频id
def get_favorite_list_video_id(favorite_id):
    return [x.video_id for x in FavoriteToVideo.objects.filter(favorite_id=favorite_id)]


# 获取收藏夹内部视频的详情
def get_favorite_list_video_detail(favorite_id):
    return [Video.objects.get(id=x).to_dic() for x in get_favorite_list_video_id(favorite_id)]


# 获取自己所有收藏夹以及内部的详细信息
def get_favorite_list_detail(user_id):
    return [
        {'favorite_list_detail': Favorite.objects.get(id=x).to_dic(),
         'favorite_list_video_detail': get_favorite_list_video_detail(x), 'num': len(get_favorite_list_video_detail(x))}
        for x in get_favorite_list_id(user_id)]


# 展示自己的收藏夹详情
def favorite_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        result = {'result': 1, 'message': r"获取收藏夹详情成功!", 'user': user.to_dic(),
                  'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 创建自己的收藏夹
def create_favorite(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        title = request.POST.get('title', '默认收藏夹')
        description = request.POST.get('description', 0)
        isPrivate = request.POST.get('isPrivate', False)
        # 创建收藏夹
        Favorite.objects.create(title=title, description=description, isPrivate=isPrivate, user_id=user_id)
        user.add_favorite()
        result = {'result': 1, 'message': r"创建收藏夹成功!", 'user': user.to_dic(),
                  'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 修改收藏夹描述
def change_favorite(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        favorite_id = request.POST.get('favorite_id', 0)
        title = request.POST.get('title', '默认收藏夹')
        description = request.POST.get('description', 0)
        isPrivate = request.POST.get('isPrivate', False)
        if favorite_id == 0:
            result = {'result': 0, 'message': r"请先选择一个收藏夹!"}
            return JsonResponse(result)
        favorite = Favorite.objects.get(id=favorite_id)
        favorite.title = title
        favorite.description = description
        favorite.isPrivate = isPrivate
        favorite.save()
        result = {'result': 1, 'message': r"修改收藏夹信息成功！", "user": user.to_dic(),
                  "station_message": list_message(user_id), 'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 收藏视频
def collect_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        favorite_id = request.POST.get('favorite_id', '')
        video_id = request.POST.get('video_id', '')
        # 先判断视频状态
        need_verify(video_id)
        if FavoriteToVideo.objects.filter(favorite_id=favorite_id, video_id=video_id).exists():
            result = {'result': 0, 'message': r"已经收藏过，请不要重复收藏!", "user": user.to_dic(),
                      "station_message": list_message(user_id),
                      'favorite_list_detail': get_favorite_list_detail(user_id)}
            return JsonResponse(result)
        FavoriteToVideo.objects.create(favorite_id=favorite_id, video_id=video_id)
        # 视频状态添加
        video = Video.objects.get(id=video_id)
        video.add_collect()

        # 视频上传者状态添加
        upload_user = Video.objects.get(id=video_id).user
        upload_user.add_collect()

        # 发送站内信
        title = "视频收获收藏啦！"
        content = "亲爱的" + upload_user.username + ''' 你好呀!\n你发布的视频有好多好朋友的收藏了，不好奇是哪位嘛(有可能ta在默默关注你呢~'''
        create_message(upload_user.id, title, content)

        result = {'result': 1, 'message': r"收藏成功！", "user": user.to_dic(), "station_message": list_message(user_id),
                  'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 取消收藏
def not_collect_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        favorite_id = request.POST.get('favorite_id', '')
        video_id = request.POST.get('video_id', '')
        if not FavoriteToVideo.objects.filter(favorite_id=favorite_id, video_id=video_id).exists():
            result = {'result': 0, 'message': r"已取消收藏，请不要重复取消!", "user": user.to_dic(),
                      "station_message": list_message(user_id)}
            return JsonResponse(result)
        FavoriteToVideo.objects.get(favorite_id=favorite_id, video_id=video_id).delete()
        # 视频状态减少
        video = Video.objects.get(id=video_id)
        video.del_collect()

        # 视频上传者状态减少
        upload_user = Video.objects.get(id=video_id).user
        upload_user.del_collect()
        result = {'result': 1, 'message': r"取消收藏成功！", "user": user.to_dic(), "station_message": list_message(user_id),
                  'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 删除收藏夹
def del_favorite(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        # 获取需要删除的收藏夹
        favorite_id = request.POST.get('favorite_id', '')
        if not Favorite.objects.filter(id=favorite_id).exists():
            result = {'result': 0, 'message': r"收藏夹已删除!请不要重复删除"}
            return JsonResponse(result)
        # 个人收藏夹数量 -1
        user.del_favorite()
        # 获取该收藏夹的所有视频id
        video_list = get_favorite_list_video_id(favorite_id)

        for every_video_id in video_list:
            FavoriteToVideo.objects.get(favorite_id=favorite_id, video_id=every_video_id).delete()
            # 视频状态减少
            video = Video.objects.get(id=every_video_id)
            video.del_collect()

            # 视频上传者状态减少
            upload_user = Video.objects.get(id=every_video_id).user
            upload_user.del_collect()
        favorite = Favorite.objects.get(id=favorite_id)
        favorite.delete()
        result = {'result': 1, 'message': r"删除收藏夹成功！", "user": user.to_dic(), "station_message": list_message(user_id),
                  'favorite_list_detail': get_favorite_list_detail(user_id)}
        return JsonResponse(result)
