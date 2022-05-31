from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import *
from user.models import UserToVideo_like
from user.views import get_fan_list_simple
from video.models import *


# 获取投诉的视频和需要人工审核的视频
def need_verify_video_list(request):
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
        token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
        isSuperAdmin = token.get('isSuperAdmin', '')
        if not isSuperAdmin:
            result = {'result': 0, 'message': r"你没有超级管理员权限，请联系超级管理员给予权限!"}
            return JsonResponse(result)
        # 需要人工审核的视频
        # 投诉的视频
        result = {'result': 1, 'message': r'获取成功',
                  "not_read": not_read(user_id),
                  'video_audit_list': [x.to_dic() for x in Video.objects.exclude(isAudit=2)],
                  'video_complain_list':
                      [{'user_detail': User.objects.get(id=x.user_id).to_simple_dic(), 'complain_detail': x.to_dic()}
                       for x in VideoComplain.objects.all()]
                  }
        return JsonResponse(result)


# 修改自动审核或者手动调整不通过的视频
def audit_need_verify_video(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        isSuperAdmin = token.get('isSuperAdmin', '')
        if not isSuperAdmin:
            result = {'result': 0, 'message': r"你没有超级管理员权限，请联系超级管理员给予权限!"}
            return JsonResponse(result)

        video_id = request.POST.get('video_id', '')
        success = request.POST.get('success', '')
        # 创建桶对象
        bucket = Bucket()
        video = Video.objects.get(id=video_id)
        user = video.user
        user_id = user.id
        # 视频格式后缀
        suffix_video = '.' + video.video_url.split(".")[-1]
        # 如果人工审核不通过
        if success == 0:
            # 自动审核不通过
            if video.isAudit == 2:
                if video.avatar_url != '':
                    suffix_avatar = '.' + video.avatar_url.split(".")[-1]
                    # 删除封面
                    bucket.delete_object("cover", str(video_id) + suffix_avatar)
                # 删除视频
                bucket.delete_object("video", str(video_id) + suffix_video)
                # 删除数据库记录
                Video.objects.get(id=video_id).delete()
                # 站内信
                title = "视频审核失败！"
                content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点违规元素,管理员看了都感觉有一点不合适呢！\n下次不要再上传这类的视频了哟，这次就算了嘿嘿~'
                create_message(user_id, title, content)
                # 删除本地文件
                os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + suffix_video))
                result = {'result': 1, 'message': r"审核完毕，成功删除该视频"}
                return JsonResponse(result)
            # 如果是管理员手动调整该视频为不通过
            elif video.isAudit == 3:
                suffix_avatar = '.' + video.avatar_url.split(".")[-1]
                bucket.delete_object("cover", str(video_id) + suffix_avatar)
                suffix_video = '.' + video.video_url.split(".")[-1]
                bucket.delete_object("video", str(video_id) + suffix_video)

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
                user.del_video()
                # 站内信
                title = "视频被管理员删除！"
                content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点违规元素,管理员看了都感觉有一点不合适呢！\n管理员感觉有一点不太合适，就先帮帮你删掉咯~'
                create_message(user_id, title, content)
                result = {'result': 1, 'message': r"审核完毕，成功删除该视频"}
                return JsonResponse(result)
        else:
            # 如果是自动审核不通过
            if video.isAudit == 2:
                # 调整状态
                video.isAudit = 1
                video.save()
                # 如果视频没有封面，取第一帧为封面
                if video.avatar_url == '':
                    bucket.cover_generator(video_id=str(video_id), suffix=suffix_video)
                    upload_result = bucket.upload_file("cover", str(video_id) + ".png", str(video_id) + ".png")
                    if upload_result == -1:
                        os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + ".png"))
                        # 删除视频
                        bucket.delete_object("video", str(video_id) + suffix_video)
                        # 删除数据库记录
                        Video.objects.get(id=video_id).delete()
                        # 删除本地文件
                        os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + suffix_video))
                        # 站内信
                        title = "视频人工审核出了一点小问题！"
                        content = "亲爱的" + user.username + '你好呀!\n' \
                                                          '由于您上传视频的时候没有附上封面，我们自动截取视频第一帧作为封面失败了，所以希望您可以选取一个好的图片作为视频的封面呀~'
                        create_message(user_id, title, content)
                        result = {'result': 0, 'message': r"人工审核通过，但是自动截取视频第一帧作为封面失败！"}
                        return JsonResponse(result)
                    # 删除本地的 png
                    os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + ".png"))
                    # 上传是否可以获取路径
                    url = bucket.query_object("cover", str(video_id) + ".png")
                    if not url:
                        # 删除视频
                        bucket.delete_object("video", str(video_id) + suffix_video)
                        # 删除数据库记录
                        Video.objects.get(id=video_id).delete()
                        # 删除本地文件
                        os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + suffix_video))
                        # 站内信
                        title = "视频审核处了一点差错！"
                        content = "亲爱的" + user.username + '你好呀!\n' \
                                                          '由于您上传视频的时候没有附上封面，我们自动截取视频第一帧作为封面失败了，所以希望您可以选取一个好的图片作为视频的封面呀~'
                        create_message(user_id, title, content)
                        result = {'result': 0, 'message': r"人工审核通过，自动截取视频第一帧作为封面失败！"}
                        return JsonResponse(result)

                    video.avatar_url = url
                    video.save()
                # 删除本地文件
                os.remove(os.path.join(BASE_DIR, "media/" + str(video_id) + suffix_video))
                # 视频数+1
                user.add_video()
                # 站内信
                title = "视频发布成功！"
                content = "亲爱的" + user.username + '你好呀!\n' \
                                                  '视频审核通过啦，快和小伙伴分享分享你的视频叭~'
                create_message(user_id, title, content)

                # 给所有粉丝发站内信
                fan_list_all = get_fan_list_simple(user_id=user_id)
                for fan_id in fan_list_all:
                    title = "你关注的博主发布新视频啦！"
                    content = "亲爱的" + User.objects.get(id=fan_id).username + '你好呀!\n' \
                                                                             '你关注的博主发布新视频啦！快去看看，然后在评论区留下自己的感受叭~'
                    create_message(fan_id, title, content)
                result = {'result': 1, 'message': r"完成人工审核，审核通过", "not_read": not_read(user_id)}
                return JsonResponse(result)
            # 如果是管理员手动调整该视频为不通过
            elif video.isAudit == 3:
                video.isAudit = 1
                video.save()
                # 站内信
                title = "视频再次审核成功！"
                content = "亲爱的" + user.username + '你好呀!\n' \
                                                  '视频审核通过啦，快和小伙伴分享分享你的视频叭~'
                create_message(user_id, title, content)
                result = {'result': 1, 'message': r"完成人工审核，审核通过", "not_read": not_read(user_id)}
                return JsonResponse(result)

# def audit_tag(request):
#     if request.method == 'POST':
#         # 检查表单信息
#         JWT = request.POST.get('JWT', '')
#         try:
#             token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
#             user_id = token.get('user_id', '')
#             user = User.objects.get(id=user_id)
#         except Exception as e:
#             result = {'result': 0, 'message': r"请先登录!"}
#             return JsonResponse(result)
#         token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
#         isSuperAdmin = token.get('isSuperAdmin', '')
#         if not isSuperAdmin:
#             result = {'result': 0, 'message': r"你没有超级管理员权限，请联系超级管理员给予权限!"}
#             return JsonResponse(result)
#         result = {'result': 1, 'message': r'获取成功',
#                   'unaudited_tag_list': list(UnAuditedTag.objects.all().values())}
#         return JsonResponse(result)
#
#
# def move_tag(request):
#     if request.method == 'POST':
#         # 检查表单信息
#         JWT = request.POST.get('JWT', '')
#         try:
#             token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
#             user_id = token.get('user_id', '')
#             user = User.objects.get(id=user_id)
#         except Exception as e:
#             result = {'result': 0, 'message': r"请先登录!"}
#             return JsonResponse(result)
#         token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
#         isSuperAdmin = token.get('isSuperAdmin', '')
#         if not isSuperAdmin:
#             result = {'result': 0, 'message': r"你没有超级管理员权限，请联系超级管理员给予权限!"}
#             return JsonResponse(result)
#         tag = request.POST.get('tag', '')
#         if tag != '':
#             UnAuditedTag.objects.filter(tag=tag).delete()
#             AuditedTag.objects.create(tag=tag)
#             result = {'result': 1, 'message': r'添加标签成功'}
#         else:
#             result = {'result': 0, 'message': r'添加标签失败'}
#         return JsonResponse(result)
