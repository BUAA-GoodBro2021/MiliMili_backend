from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import *
from user.models import *
from video.models import *


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

        if title == '' or description == '' or zone == '':
            result = {'result': 0, 'message': r"视频标题或描述或分区不能为空!", "station_message": list_message(user.id)}
            return JsonResponse(result)

        # 常见对象存储的对象
        bucket = Bucket()
        # 创建一个视频对象
        video = Video.objects.create(title=title, description=description, zone=zone, user_id=user_id)
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

        # 判断是否已经点赞过
        if UserToVideo_like.objects.filter(user_id=user_id, video_id=video_id).exists():
            result = {'result': 0, 'message': r"已经点赞过，请不要重复点赞!"}
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

        result = {'result': 1, 'message': r"点赞成功！", "user": user.to_dic(), "station_message": list_message(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


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
        UserToVideo_like.objects.get(user_id=user_id, video_id=video_id).delete()
        video = Video.objects.get(id=video_id)
        video.del_like()
        # 获取视频的发布者 其收获的点赞数-1
        upload_user = video.user
        upload_user.del_like()

        result = {'result': 1, 'message': r"取消成功！", "user": user.to_dic(), "station_message": list_message(user_id)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
