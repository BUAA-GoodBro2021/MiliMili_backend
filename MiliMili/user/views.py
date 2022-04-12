from MiliMili.settings import BASE_DIR
from bucket_manager.Bucket import Bucket
from sending.views import *
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
            'isSuperAdmin': user.isSuperAdmin
        }
        # 令牌
        JWT = jwt.encode(token, SECRET_KEY, algorithm='HS256')
        result = {'result': 1, 'message': r"登录成功！", 'JWT': JWT, 'user': user.to_dic(),
                  "station_message": list_message(user.id)}
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
            result = {'result': 0, 'message': r"请先登录!"}
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


def upload_file(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)
        username = request.POST.get('username', '')

        if len(username) == 0:
            result = {'result': 0, 'message': r"用户名不可以为空!"}
            return JsonResponse(result)

        if User.objects.filter(username=username, isActive=True).exists():
            result = {'result': 0, 'message': r'用户已存在!'}
            return JsonResponse(result)
        user.username = username
        user.save()

        # 站内信
        title = "用户名修改成功！"
        content = "亲爱的" + user.username + ''' 你好呀!\n用户名已经更新啦，快去给好朋友分享分享叭！'''
        create_message(user_id, title, content)

        result = {'result': 1, 'message': r"修改用户名成功!", "user": user.to_dic(),
                  "station_message": list_message(user.id)}
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
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        # 获取用户上传的头像并检验是否符合要求
        avatar = request.FILES.get("avatar", None)
        if not avatar:
            result = {'result': 0, 'message': r"请上传图片！"}
            return JsonResponse(result)
        if avatar.size > 1024 * 1024:
            result = {'result': 0, 'message': r"图片不能超过1M！"}
            return JsonResponse(result)
        # 获取文件尾缀并修改名称
        suffix = '.' + avatar.name.split(".")[-1]
        avatar.name = str(user_id) + suffix
        # 保存到本地
        user.avatar = avatar
        user.save()

        # 常见对象存储的对象
        bucket = Bucket()

        # 先生成一个随机 Key 保存在桶中进行审核
        key = create_code()
        upload_result = bucket.upload_file("avatar", key + suffix, avatar.name)
        # 上传审核
        if upload_result == -1:
            result = {'result': 0, 'message': r"上传失败！"}
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
            return JsonResponse(result)

        # 审核
        audit_dic = bucket.image_audit("avatar", key + suffix)
        if audit_dic.get("result") != 0:
            result = {'result': 0, 'message': r"审核失败！", "user": user.to_dic(), "station_message": list_message(user.id)}
            # 删除审核对象
            bucket.delete_object("avatar", key + suffix)
            # 删除本地对象
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
            # 站内信
            title = "头像审核失败！"
            content = "亲爱的" + user.username + ' 你好呀!\n头像好像带有一点'+audit_dic.get("label")+'呢！'
            create_message(user_id, title, content)
            return JsonResponse(result)

        # 删除审核对象
        bucket.delete_object("avatar", key + suffix)

        # 判断用户是不是默认头像   如果不是，要删除以前的
        if user.avatar_url != "https://global-1309504341.cos.ap-beijing.myqcloud.com/default.jpg":
            bucket.delete_object("avatar", str(user_id) + suffix)

        # 上传是否成功
        upload_result = bucket.upload_file("avatar", str(user_id) + suffix, avatar.name)
        if upload_result == -1:
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
            result = {'result': 0, 'message': r"上传失败！"}
            return JsonResponse(result)

        # 上传是否可以获取路径
        url = bucket.query_object("avatar", str(user_id) + suffix)
        if not url:
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
            result = {'result': 0, 'message': r"上传失败！"}
            return JsonResponse(result)
        # 获取对象存储的桶地址
        user.avatar_url = url
        # 删除本地文件
        os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))

        # 站内信
        title = "上传头像成功！"
        content = "亲爱的" + user.username + ''' 你好呀!\n头像已经更新啦，快去给好朋友分享分享叭！'''
        create_message(user_id, title, content)

        result = {'result': 1, 'message': r"上传成功！", "user": user.to_dic(), "station_message": list_message(user.id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
