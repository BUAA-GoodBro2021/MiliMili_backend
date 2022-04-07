from django.http import JsonResponse

from sending.views import send_email
from user.models import User


# Create your views here.


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

        # 发送邮件激活
        status = int(request.POST.get('status', 0))
        # 发送邮件
        print(status)
        if status == 0:
            print(status)
            # 申请一个伪用户
            user = User.objects.create(username=username, password=password1, isActive=False)
            # 需要加密的信息
            token = {
                'user_id': user.id,
            }
            print(status)
            # 发送邮件
            send_result = send_email(token, email)
            if not send_result:
                result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
                return JsonResponse(result)
            else:
                result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.'}
                return JsonResponse(result)
        else:
            try:
                # 把伪用户转变为真正的用户
                user = User.objects.get(username=username, isActive=True)
                user.email = email
                user.save()
                user = User.objects.get(username=username, isActive=False)
                user.delete()
                result = {'result': 1, 'message': r'注册成功!'}
                return JsonResponse(result)
            except Exception as e:
                result = {'result': 0, 'message': r'用户已存在!'}
                return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
