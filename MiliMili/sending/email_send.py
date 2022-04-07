from random import Random  # 用于生成随机码

from django.conf import settings  # setting.py添加的的配置信息
from django.core.mail import EmailMessage  # 发送邮件模块
from django.template import loader  # 加载模板

from .models import *


# 生成随机字符串
def create_code(randomlength=6):
    str_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str_code += chars[random.randint(0, length)]
    return str_code


def send_code_email(email):
    email_code = create_code(6)
    newcode = Email_code()
    newcode.email_code = email_code
    newcode.save()

    email_title = r"开源社区图谱网站注册激活验证码"

    data = {'email_code1': email_code, 'email_code2': email_code}
    email_body = loader.render_to_string('EmailContent-plus.html', data)

    msg = EmailMessage(email_title, email_body, settings.EMAIL_HOST_USER, [email])
    msg.content_subtype = 'html'
    send_status = msg.send()
    return send_status


# 检查验证码是否正确
def check_code(email_code):
    if not Email_code.objects.filter(email_code=email_code).exists():
        return False
    else:
        Email_code.objects.filter(email_code=email_code).delete()
        return True
