from sending.views import *
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
                  'video_audit_list': [x.to_dic() for x in Video.objects.filter(isAudit=2)],
                  'video_complain_list':
                      [{'user_detail': User.objects.get(id=x.user_id).to_dic(), 'complain_detail': x.to_dic()} for x in
                       VideoComplain.objects.all()]
                  }
        return JsonResponse(result)


def audit_tag(request):
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
        result = {'result': 1, 'message': r'获取成功',
                  'unaudited_tag_list': list(UnAuditedTag.objects.all().values())}
        return JsonResponse(result)


def move_tag(request):
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
        tag = request.POST.get('tag', '')
        if tag != '':
            UnAuditedTag.objects.filter(tag=tag).delete()
            AuditedTag.objects.create(tag=tag)
            result = {'result': 1, 'message': r'添加标签成功'}
        else:
            result = {'result': 0, 'message': r'添加标签失败'}
        return JsonResponse(result)
