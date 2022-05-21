from video.views import *


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
        result = {'result': 1, 'message': r"登录成功！", 'JWT': JWT, "not_read": not_read(user.id), 'user': user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def find_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        if not User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': r'用户名不存在!'}
            return JsonResponse(result)
        user = User.objects.get(username=username)
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
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.', "not_read": not_read(user.id)}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def change_file(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"请先登录!"}
            return JsonResponse(result)

        # 获取用户名
        username = request.POST.get('username', '')

        # 用户名不允许为空
        if len(username) == 0:
            result = {'result': 0, 'message': r"用户名不可以为空!"}
            return JsonResponse(result)

        # 用户名如果没有改变，不需要检查用户名是否已存在
        if username != User.objects.get(id=user_id).username:
            if User.objects.filter(username=username, isActive=True).exists():
                result = {'result': 0, 'message': r'用户名已存在!'}
                return JsonResponse(result)

        # 获取用户上传头像
        avatar = request.FILES.get("avatar", None)
        if avatar:
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
                result = {'result': 0, 'message': r"审核失败！", "user": user.to_dic(),
                          "station_message": list_message(user.id)}
                # 删除审核对象
                bucket.delete_object("avatar", key + suffix)
                # 删除本地对象
                os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))
                # 站内信
                title = "头像审核失败！"
                content = "亲爱的" + user.username + ' 你好呀!\n头像好像带有一点' + audit_dic.get("label") + '呢！'
                create_message(user_id, title, content)
                return JsonResponse(result)

            # 删除审核对象
            bucket.delete_object("avatar", key + suffix)

            # 判断用户是不是默认头像   如果不是，要删除以前的
            if user.avatar_url != default_avatar_url:
                try:
                    bucket.delete_object("avatar", str(user_id) + ".png")
                except Expression:
                    pass
                try:
                    bucket.delete_object("avatar", str(user_id) + ".jpg")
                except Expression:
                    pass
                try:
                    bucket.delete_object("avatar", str(user_id) + ".jpeg")
                except Expression:
                    pass

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
            user.save()
            # 删除本地文件
            os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))

        # 获取昵称,性别，生日
        nickname = request.POST.get('nickname', '')
        sex = request.POST.get('sex', '')
        signature = request.POST.get('signature', '')
        birthday = request.POST.get('birthday', '')
        location = request.POST.get('location', '')

        user.username = username
        user.nickname = nickname
        user.sex = sex
        user.signature = signature
        user.birthday = birthday
        user.location = location
        user.save()
        # 站内信
        title = "用户个人信息修改成功！"
        content = "亲爱的" + user.username + ''' 你好呀!\n个人资料已经更新啦，快去给好朋友分享分享叭！'''
        create_message(user_id, title, content)

        result = {'result': 1, 'message': r"修改用户个人资料成功!", "not_read": not_read(user_id), "user": user.to_dic()}
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
            content = "亲爱的" + user.username + ' 你好呀!\n头像好像带有一点' + audit_dic.get("label") + '呢！'
            create_message(user_id, title, content)
            return JsonResponse(result)

        # 删除审核对象
        bucket.delete_object("avatar", key + suffix)

        # 判断用户是不是默认头像   如果不是，要删除以前的
        if user.avatar_url != default_avatar_url:
            try:
                bucket.delete_object("avatar", str(user_id) + ".png")
            except Expression:
                pass
            try:
                bucket.delete_object("avatar", str(user_id) + ".jpg")
            except Expression:
                pass
            try:
                bucket.delete_object("avatar", str(user_id) + ".jpeg")
            except Expression:
                pass

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
        user.save()
        # 删除本地文件
        os.remove(os.path.join(BASE_DIR, "media/" + avatar.name))

        # 站内信
        title = "上传头像成功！"
        content = "亲爱的" + user.username + ''' 你好呀!\n头像已经更新啦，快去给好朋友分享分享叭！'''
        create_message(user_id, title, content)

        result = {'result': 1, 'message': r"上传成功！", "not_read": not_read(user_id), "user": user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取个人关注列表的id
def get_follow_list_simple(user_id):
    return [x.follow_id for x in UserToFollow.objects.filter(user_id=user_id)]


# 获取个人关注列表的详情(具体信息)
def get_follow_list_detail(user_id):
    return [User.objects.get(id=x).to_dic() for x in get_follow_list_simple(user_id)]


# 获取个人粉丝列表的id
def get_fan_list_simple(user_id):
    return [x.fan_id for x in UserToFan.objects.filter(user_id=user_id)]


# 获取个人粉丝列表的详情(具体信息)
def get_fan_list_detail(user_id):
    return [User.objects.get(id=x).to_dic() for x in get_fan_list_simple(user_id)]


# 关注一个用户
def follow(request):
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

        # 获取关注用户的实体和id
        follow_id = int(request.POST.get('follow_id', ''))
        try:
            follow_user = User.objects.get(id=follow_id)
        except Exception as e:
            result = {'result': 0, 'message': r"关注的用户不存在!"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id in get_follow_list_simple(user_id):
            result = {'result': 0, 'message': r"已关注该用户!"}
            return JsonResponse(result)

        # 添加双向记录
        UserToFollow.objects.create(user_id=user_id, follow_id=follow_id)
        UserToFan.objects.create(user_id=follow_id, fan_id=user_id)

        # 关注数+1 , 粉丝数+1
        user.add_follow()
        follow_user.add_fan()

        # 发送站内信
        title = "又有好朋友关注你啦！"
        content = "亲爱的" + follow_user.username + ''' 你好呀!\n又有一位好朋友关注了你，不打算看看是哪位嘛！'''
        create_message(follow_id, title, content, 5, user_id)

        result = {'result': 1, 'message': r"关注成功！", "not_read": not_read(user_id), "user": user.to_dic()}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 取消关注
def unfollow(request):
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

        # 获取取消关注用户的实体和id
        follow_id = int(request.POST.get('follow_id', ''))
        try:
            follow_user = User.objects.get(id=follow_id)
        except Exception as e:
            result = {'result': 0, 'message': r"取消关注的用户不存在!"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id not in get_follow_list_simple(user_id):
            result = {'result': 0, 'message': r"从未关注过该用户!"}
            return JsonResponse(result)

        # 删除双向记录
        UserToFollow.objects.get(user_id=user_id, follow_id=follow_id).delete()
        UserToFan.objects.create(user_id=follow_id, fan_id=user_id).delete()

        # 关注数-1 , 粉丝数-1
        user.del_follow()
        follow_user.del_fan()

        result = {'result': 1, 'message': r"取消成功！", "not_read": not_read(user_id), "user": user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 展示关注列表
def follow_list(request):
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

        result = {'result': 1, 'message': r"获取关注列表成功！", "not_read": not_read(user_id), "user": user.to_dic(),
                  "follow_list": get_follow_list_detail(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 展示粉丝列表
def fan_list(request):
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

        result = {'result': 1, 'message': r"获取粉丝列表成功！", "not_read": not_read(user_id), "user": user.to_dic(),
                  "fan_list": get_fan_list_detail(user_id), }
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def find_history(request):
    from video.models import Video
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
        # TODO 视频历史记录莫得时间（）
        history = list(UserToSearchHistory.objects.filter(user_id=user_id).order_by('-id').values())
        video_list = []
        for h in history:
            video_list.append(Video.objects.get(id=h.get('video_id')).values())
        result = {'result': 1, 'message': r'获取历史记录成功', "not_read": not_read(user_id), 'video_list': video_list}
    else:
        result = {'result': 0, 'message': r'获取历史记录失败'}
    return JsonResponse(result)


# 获取自己正常的视频列表
def video_list(request):
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
        result = {'result': 1, 'message': r"获取视频列表成功！", "not_read": not_read(user_id), "user": user.to_dic(),
                  "video_list": [x.to_dic() for x in Video.objects.filter(user_id=user_id, isAudit=1, need_verify=0)],
                  "video_num": len(Video.objects.filter(user_id=user_id, isAudit=1, need_verify=0))}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取自己审核状态的视频列表
def video_audit_list(request):
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
        video_all_list = Video.objects.filter(user_id=user_id)
        result = {'result': 1, 'message': r"获取视频列表成功！", "not_read": not_read(user_id), "user": user.to_dic(),
                  "video_list": [x.to_dic() for x in video_all_list.filter(user_id=user_id)],
                  "video_num": len(video_all_list.filter(user_id=user_id)),
                  "video_list_auditing": [x.to_dic() for x in video_all_list.filter(isAudit=0)],
                  "video_auditing_num": len(video_all_list.filter(isAudit=0)),
                  "video_list_need_audit": [x.to_dic() for x in video_all_list.filter(isAudit=2)],
                  "video_need_audit_num": len(video_all_list.filter(isAudit=2)),
                  "video_list_audited": [x.to_dic() for x in video_all_list.filter(isAudit=1)],
                  "video_audited_num": len(video_all_list.filter(isAudit=1))}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取自己投诉状态列表
def complain_list(request):
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
        video_complain_list = VideoComplain.objects.all()
        result = {'result': 1, 'message': r'获取成功', "not_read": not_read(user_id),
                  'video_complain_list': [x.to_dic() for x in video_complain_list],
                  'video_complain_num': len(video_complain_list),
                  'video_complaining_list': [x.to_dic() for x in video_complain_list.filter(verify_result=0)],
                  'video_complaining_num': len(video_complain_list.filter(verify_result=0)),
                  'video_finish_list': [x.to_dic() for x in video_complain_list.exclude(verify_result=0)],
                  'video_finish_num': len(video_complain_list.exclude(verify_result=0)),
                  }
        return JsonResponse(result)


def all_list(request):
    if request.method == 'POST':
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

            result = {'result': 1, 'message': r"获取详情列表成功！", "not_read": not_read(user_id), "user": user.to_dic(),
                      "follow_list": get_follow_list_detail(user_id),
                      "fan_list": get_fan_list_detail(user_id),
                      "video_list": [x.to_dic() for x in Video.objects.filter(user_id=user_id)],
                      "video_num": len(Video.objects.filter(user_id=user_id)),
                      }
            return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 展示up主粉丝列表
def up_fan_list(request):
    if request.method == 'POST':
        # 检查表单信息
        up_user_id = request.POST.get('up_user_id', '')
        try:
            up_user = User.objects.get(id=up_user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"获取粉丝列表失败！"}
            return JsonResponse(result)
        result = {'result': 1, 'message': r"获取粉丝列表成功！", "user": up_user.to_dic(),
                  "fan_list": get_fan_list_detail(up_user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 展示up主关注列表
def up_follow_list(request):
    if request.method == 'POST':
        # 检查表单信息
        up_user_id = request.POST.get('up_user_id', '')
        try:
            up_user = User.objects.get(id=up_user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"获取关注列表失败！"}
            return JsonResponse(result)

        result = {'result': 1, 'message': r"获取关注列表成功！", "user": up_user.to_dic(),
                  "follow_list": get_follow_list_detail(up_user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取up主视频列表
def up_video_list(request):
    if request.method == 'POST':
        # 检查表单信息
        up_user_id = request.POST.get('up_user_id', '')
        try:
            up_user = User.objects.get(id=up_user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"获取关注列表失败！"}
            return JsonResponse(result)
        result = {'result': 1, 'message': r"获取视频列表成功！", "user": up_user.to_dic(),
                  "video_list": [x.to_dic() for x in
                                 Video.objects.filter(user_id=up_user_id, isAudit=1, need_verify=0)],
                  "video_num": len(Video.objects.filter(user_id=up_user_id, isAudit=1, need_verify=0))}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取公开收藏夹详情
def up_public_favorite(request):
    if request.method == 'POST':
        # 检查表单信息
        up_user_id = request.POST.get('up_user_id', '')
        try:
            up_user = User.objects.get(id=up_user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"获取关注的收藏夹详情失败！"}
            return JsonResponse(result)
        result = {'result': 1, 'message': r"获取收藏夹详情成功!", 'user': up_user.to_dic(),
                  'favorite_list_detail': get_favorite_list_detail(up_user_id, 0)}
        return JsonResponse(result)


def up_all_list(request):
    if request.method == 'POST':
        # 检查表单信息
        up_user_id = request.POST.get('up_user_id', '')
        try:
            up_user = User.objects.get(id=up_user_id)
        except Exception as e:
            result = {'result': 0, 'message': r"获取详情列表失败！"}
            return JsonResponse(result)
        result = {'result': 1, 'message': r"获取详情列表成功！", "user": up_user.to_dic(),
                  "follow_list": get_follow_list_detail(up_user_id),
                  "fan_list": get_fan_list_detail(up_user_id),
                  "video_list": [x.to_dic() for x in
                                 Video.objects.filter(user_id=up_user_id, isAudit=1, need_verify=0)],
                  "video_num": len(Video.objects.filter(user_id=up_user_id, isAudit=1, need_verify=0)),
                  'favorite_list_detail': get_favorite_list_detail(up_user_id, 0)}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
