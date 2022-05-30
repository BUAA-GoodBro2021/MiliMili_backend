import os
import platform
import random
from random import Random

import jwt

from django.core.mail import EmailMessage
from django.db.models import *
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

from MiliMili.settings import SECRET_KEY
from key import *
from sending.models import Message
from user.models import User


# 返回个人的站内信和个数
def list_message(user_id):
    # 获取站内信
    message_filter = Message.objects.filter(user_id=user_id)
    message_list = [x.to_dic() for x in message_filter]
    # 统计未读数目
    not_read_num = message_filter.filter(isRead=False).aggregate(not_read_num=Count('title'))
    return {
        "message_list": message_list,
        "not_read_num": not_read_num
    }


def not_read(user_id):
    message_filter = Message.objects.filter(user_id=user_id, isRead=False)
    if not message_filter.exists():
        return 0
    else:
        return 1


# 返回不分类的站内信(有总共未读个数)
def list_message_simple(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        message_filter = Message.objects.filter(user_id=user_id)
        message_list = [x.to_dic() for x in message_filter]
        # 统计未读数目
        not_read_num = message_filter.filter(isRead=False).aggregate(not_read_num=Count('title'))
        result = {'result': 1, 'message': r"获取不分类分类私信成功!", "not_read": not_read(user_id), "message_list": message_list,
                  "not_read_num": not_read_num}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 返回分类之后的站内信
def list_message_detail(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        # 0 - 系统通知 1 - 评论回复我的 2 - 收到的赞 3 - 收藏 4 - 我的消息(私信) 5 - 新增粉丝
        message_filter = Message.objects.filter(user_id=user_id)
        message_sys = message_filter.filter(from_type=0)
        message_reply = message_filter.filter(from_type=1)
        message_like = message_filter.filter(from_type=2)
        message_collect = message_filter.filter(from_type=3)
        message_self = message_filter.filter(from_type=4)
        message_fan = message_filter.filter(from_type=5)
        result = {'result': 1, 'message': r"获取分类私信详情成功!",
                  "not_read": not_read(user_id),
                  "message_sys": [x.to_dic() for x in message_sys],
                  "message_reply": [x.to_dic() for x in message_reply],
                  "message_like": [x.to_dic() for x in message_like],
                  "message_collect": [x.to_dic() for x in message_collect],
                  "message_self": [x.to_dic() for x in message_self],
                  "message_fan": [x.to_dic() for x in message_fan],
                  }

        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 创造一个人的站内信
def create_message(user_id, title, content, from_type=0, from_id=1):
    message = Message()
    message.title = title
    message.content = content
    message.user_id = user_id
    message.isRead = False
    message.from_id = from_id
    message.from_type = from_type
    message.save()


# 向有一个用户发送私信
def send_message(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        if len(title) == 0 or len(content) == 0:
            result = {'result': 0, 'message': r"标题或者内容不能为空!"}
            return JsonResponse(result)
        send_user_id = request.POST.get('send_user_id', '')
        create_message(send_user_id, title, content, 4, user_id)
        result = {'result': 1, 'message': r"发送私信成功!", "not_read": not_read(user_id), "user": user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户读站内信
def read_message(request):
    # 检查表单信息
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        message_id = request.POST.get('message_id', '')

        try:
            message = Message.objects.get(id=message_id)
        except Exception as e:
            result = {'result': 0, 'message': r"该站内信不存在!"}
            return JsonResponse(result)
        if message.user_id != user_id:
            result = {'result': 0, 'message': r"用户错误!"}
            return JsonResponse(result)
        message.isRead = True
        message.save()
        result = {'result': 1, 'message': r"已读信息!", "not_read": not_read(user_id), "user": user.to_dic(),
                  "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户一次性全部已读
def read_all_message(request):
    # 检查表单信息
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        Message.objects.filter(user_id=user_id).update(isRead=True)
        result = {'result': 1, 'message': r"已读全部信息!", "not_read": not_read(user_id), "user": user.to_dic(),
                  "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户删除站内信
def del_message(request):
    # 检查表单信息
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        message_id = request.POST.get('message_id', '')

        try:
            message = Message.objects.get(id=message_id)
        except Exception as e:
            result = {'result': 0, 'message': r"该站内信不存在!"}
            return JsonResponse(result)
        if message.user_id != user_id:
            result = {'result': 0, 'message': r"用户错误!"}
            return JsonResponse(result)
        message.delete()
        result = {'result': 1, 'message': r"删除成功!", "not_read": not_read(user_id), "user": user.to_dic(),
                  "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户删除全部站内信
def del_all_message(request):
    # 检查表单信息
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        Message.objects.filter(user_id=user_id).delete()
        result = {'result': 1, 'message': r"全部删除成功!", "not_read": not_read(user_id), "user": user.to_dic(),
                  "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 发送真实邮件
def send_email(token, email, title):
    # 验证路由
    url = jwt.encode(token, SECRET_KEY, algorithm='HS256')  # 加密生成字符串
    if platform.system() == "Linux":
        url = os.path.join("https://milimili.super2021.com/api/sending/", url)
    else:
        url = os.path.join("http://127.0.0.1/api/sending/", url)
    data = {'url': url}
    email_title = email_body = ''
    if title == 'active':
        email_title = r"欢迎注册MiliMili短视频分享平台"
        email_body = loader.render_to_string('EmailContent-register.html', data)
    elif title == 'find':
        email_title = r"MiliMili重设密码"
        email_body = loader.render_to_string('EmailContent-find.html', data)
    try:
        msg = EmailMessage(email_title, email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        return send_status
    except Exception as e:
        return 0


def active(request, url):
    # 获取token信息
    token = jwt.decode(url, SECRET_KEY, algorithms=['HS256'])
    user_id = token.get('user_id')
    # 邮件的链接地址
    data = {'url': 'https://milimili.super2021.com'}
    # 获取到用户
    user = User.objects.get(id=user_id)
    username = user.username

    # 激活邮箱
    if 'email' in token.keys():
        email = token.get('email')
        # 激活用户 验证邮箱
        user.isActive = True
        user.email = email
        avatar_url = default_avatar_url_match + str(random.choice(range(1, 51))) + '.png'
        user.avatar_url = avatar_url
        user.save()
        # 删除其他伪用户
        user = User.objects.filter(username=username, isActive=False)

        # 发送站内信
        title = "欢迎注册MiliMili短视频分享平台！"
        content = "亲爱的" + username + ''' 你好呀!\n
             非常高兴可以成为我们MiliMili大家庭中的一员呢！
             MiliMili是super2021组织中MiliMili团队打造的一个短视频分享平台，里面有很多志同道合的好朋友，快去探索叭！
        '''
        create_message(user_id, title, content)

        if user.exists():
            user.delete()

        # 返回注册成功的界面
        data["title"] = "感谢注册"
        data["message"] = "注册MiliMili短视频分享平台成功！"
        return render(request, 'EmailContent-check.html', data)

    # 重设密码
    if 'password' in token.keys():
        password = token.get('password')
        # 修改密码
        user.password = password
        user.save()

        # 发送站内信
        title = "重设密码成功！"
        content = "亲爱的" + username + ''' 你好呀!\n重设密码成功哟！如果发现本人没有操作，那大概率是密码泄露啦！'''
        create_message(user_id, title, content)

        # 返回修改成功的界面
        data["title"] = "修改成功"
        data["message"] = "修改密码成功！"
        return render(request, 'EmailContent-check.html', data)


# 生成随机字符串
def create_code(random_length=6):
    str_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str_code += chars[random.randint(0, length)]
    return str_code
