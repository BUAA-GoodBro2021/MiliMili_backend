import os

import jwt
from django.conf.global_settings import SECRET_KEY
from django.http import JsonResponse

from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import send_email
from user.models import User


def register(request):
    if request.method == 'POST':
        # 获取表单信息
        username = request.POST.get('username', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(username) == 0 or len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if User.objects.filter(username=username, isActive=True).exists():
            result = {'result': 0, 'message': r'用户已存在!'}
            return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        email = request.POST.get('email', '')

        if len(email) == 0:
            result = {'result': 0, 'message': r'邮箱不允许为空!'}
            return JsonResponse(result)

        # 验证部分
        user = User.objects.create(username=username, password=password1, isActive=False)
        # 需要加密的信息
        token = {
            'user_id': user.id,
            'email': email,
        }
        # 发送邮件
        send_result = send_email(token, email, 'active')
        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def login(request):
    if request.method == 'POST':
        # 获取表单信息
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if len(username) == 0 or len(password) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if not User.objects.filter(username=username, isActive=True).exists():
            result = {'result': 0, 'message': r'用户不存在!'}
            return JsonResponse(result)

        user = User.objects.get(username=username, isActive=True)

        if user.password != password:
            result = {'result': 0, 'message': r'用户名或者密码有误!'}
            return JsonResponse(result)
        # 需要加密的信息
        token = {
            'user_id': user.id,
        }
        # 令牌
        JWT = jwt.encode(token, SECRET_KEY, algorithm='HS256')
        result = {'result': 1, 'message': r"登录成功！", 'JWT': JWT, 'user': user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def findPassword(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"验证失败，清重新登录，检查是否擅自修改过token！"}
            return JsonResponse(result)
        # 获取密码
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        email = user.email
        # 需要加密的信息
        token = {
            'user_id': user.id,
            'password': password1,
        }
        # 发送邮件
        send_result = send_email(token, email, 'find')
        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def upload_avatar(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"验证失败，清重新登录，或者检查是否擅自修改过token！"}
            return JsonResponse(result)

        avatar = request.FILES.get("avatar", None)
        if not avatar:
            result = {'result': 0, 'message': r"请上传图片！"}
            JsonResponse(result)
        if avatar.size > 1024 * 2:
            result = {'result': 0, 'message': r"图片不能超过2M！"}
            JsonResponse(result)

        # 重命名文件并保存到本地
        avatar.name = "MiliMili-logo.png"
        user.avatar = avatar
        user.save()

        # 上传文件
        bucket = Bucket()
        upload_result = bucket.upload_file("avatar", str(user_id), avatar.name)
        if upload_result == -1:
            result = {'result': 0, 'message': r"上传失败！"}
            JsonResponse(result)

        # url = bucket.query_object("avatar", str(user_id))
        # if not url:
        #     result = {'result': 0, 'message': r"上传失败！"}
        #     JsonResponse(result)
        #
        # # 获取对象存储的桶地址
        # user.avatar_url = url
        # # 删除本地文件
        # os.remove(os.path.join(BASE_DIR, "media\\" + avatar.name))
        # user.avatar = None
        # user.save()

        result = {'result': 1, 'message': r"上传成功！"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
