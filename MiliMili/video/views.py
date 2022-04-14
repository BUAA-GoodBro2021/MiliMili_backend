import os

import jwt
from django.conf.global_settings import SECRET_KEY
from django.http import JsonResponse
from django.shortcuts import render

from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import create_code, list_message, create_message
from user.models import *
from video.models import Video


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
            result = {'result': 0, 'message': r"视频标题或描述或分区不能为空!"}
            return JsonResponse(result)

        # 创建一个视频对象
        video = Video.objects.create(title=title, description=description, zone=zone, user_id=user_id)
        video_id = video.id
        # 获取用户上传的封面并检验是否符合要求
        avatar = request.FILES.get("avatar", None)
        # 如果有封面，审核封面
        if avatar:
            if avatar.size > 1024 * 1024:
                Video.objects.get(id=video_id).delete()
                result = {'result': 0, 'message': r"图片不能超过1M！"}
                return JsonResponse(result)
            # 获取文件尾缀并修改名称
            suffix = '.' + avatar.name.split(".")[-1]
            avatar.name = str(video.id) + suffix
            # 保存到本地
            video.avatar = avatar
            video.save()

            # 常见对象存储的对象
            bucket = Bucket()

            # 先生成一个随机 Key 保存在桶中进行审核
            key = create_code()
            upload_result = bucket.upload_file("cover", key + suffix, avatar.name)
            # 上传审核
            if upload_result == -1:
                result = {'result': 0, 'message': r"上传失败！"}
                Video.objects.get(id=video_id).delete()
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                return JsonResponse(result)

            # 审核
            audit_dic = bucket.image_audit("cover", key + suffix)
            if audit_dic.get("result") != 0:
                result = {'result': 0, 'message': r"视频封面审核失败！"}
                # 删除审核对象
                bucket.delete_object("avatar", key + suffix)
                # 删除本地对象
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                # 删除创建的视频模型
                Video.objects.get(id=video_id).delete()
                # 站内信
                title = "视频封面审核失败！"
                content = "亲爱的" + user.username + ' 你好呀!\n视频封面好像带有一点' + audit_dic.get("label") + '呢！'
                create_message(user_id, title, content)
                return JsonResponse(result)

