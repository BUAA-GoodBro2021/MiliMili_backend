import os
import platform

import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader

from user.models import User


def send_email(token, email):
    # 验证路由
    url = jwt.encode(token, 'secret', algorithm='HS256')  # 加密生成字符串
    if platform.system() == "Linux":
        url = os.path.join("https://milimili.super2021.com/api/sending/", url)
    else:
        url = os.path.join("http://127.0.0.1/api/sending/", url)
    data = {'url': url}
    email_title = r"MiliMili邮箱激活"
    email_body = loader.render_to_string('EmailContent-cloud.html', data)
    try:
        msg = EmailMessage(email_title, email_body, settings.EMAIL_HOST_USER, [email])
        msg.content_subtype = 'html'
        send_status = msg.send()
        return send_status
    except Exception as e:
        return 0


def active(request, url):
    token = jwt.decode(url, 'secret', algorithms=['HS256'])
    user_id = token.get('user_id')
    user = User.objects.get(id=user_id)
    user.isActive = True
    user.save()
