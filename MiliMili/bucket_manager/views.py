import json

from user.views import *
from video.models import *


def callback(request):
    bucket = Bucket()
    if request.method == 'POST':
        body = json.loads(request.body)
        audit_result = bucket.video_audit_query(body)
        result = audit_result.get("result")
        job_id = audit_result.get("job_id")
        label = audit_result.get("label")
        jobToVideo = JobToVideo.objects.get(job_id=job_id)
        video_id = jobToVideo.video_id
        video = Video.objects.get(id=video_id)
        user = video.user
        user_id = user.id
        # 删除审核记录
        JobToVideo.objects.get(job_id=job_id).delete()
        # 视频格式后缀
        suffix_video = '.' + video.video_url.split(".")[-1]
        # 审核不通过
        if result == 1:
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
            content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点' + label + '呢！\n下次不要再上传这类的视频了哟，这次就算了嘿嘿~'
            create_message(user_id, title, content)
            result = {'result': 0, 'message': r"上传失败！"}
            return JsonResponse(result)
        if result == 2:
            video.isAudit = 2
            video.save()
            # 站内信
            title = "视频需要人工审核！"
            content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点' + label + '呢！\n我们需要人工再进行审核，不要着急哦~'
            create_message(user_id, title, content)
            result = {'result': 0, 'message': r"需要人工审核！"}
        if result == 0:
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
                    title = "视频审核出了一点小问题！"
                    content = "亲爱的" + user.username + '你好呀!\n' \
                                                      '由于您上传视频的时候没有附上封面，我们自动截取视频第一帧作为封面失败了，所以希望您可以选取一个好的图片作为视频的封面呀~ '
                    create_message(user_id, title, content)
                    result = {'result': 0, 'message': r"自动截取视频第一帧作为封面失败！"}
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
                                                      '由于您上传视频的时候没有附上封面，我们自动截取视频第一帧作为封面失败了，所以希望您可以选取一个好的图片作为视频的封面呀~ '
                    create_message(user_id, title, content)
                    result = {'result': 0, 'message': r"自动截取视频第一帧作为封面失败！"}
                    return JsonResponse(result)

                video.avatar_url = url
                video.save()
            # 如果已经有封面的了
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

            result = {'result': 1, 'message': r"视频发送成功！", "not_read": not_read(user_id)}
    else:
        result = {'result': -1, 'label': None, 'job_id': None}
    return JsonResponse(result)
