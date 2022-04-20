from django.http import JsonResponse
from index.ThreadController import ThreadController


def video_search(request, search_str):
    try:
        video_list = ThreadController(search_str, 'video').run()
        result = 1
        message = r'搜索视频成功'
    except Exception:
        video_list = None
        result = 0
        message = r'搜索视频失败'
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        order = request.POST.get('order', '')
        if order == 'default' or video_list is None:
            pass
        elif order == 'time':
            video_list = sorted(video_list, key=lambda x: -x.get('updated_time'))
        elif order == 'view':
            video_list = sorted(video_list, key=lambda x: -x.get('view_num'))
        else:
            pass
    else:
        pass
    result = {'result': result, 'message': message, 'list': video_list}
    return JsonResponse(result)


def user_search(request, search_str):
    try:
        user_list = ThreadController(search_str, 'user').run()
        result = 1
        message = r'搜索用户成功'
    except Exception:
        user_list = None
        result = 0
        message = r'搜索用户失败'
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        order = request.POST.get('order', '')
        if order == 'default' or user_list is None:
            pass
        elif order == 'fun':
            user_list = sorted(user_list, key=lambda x: -x.get('fun_num'))
        else:
            pass
    else:
        pass
    result = {'result': result, 'message': message, 'list': user_list}
    return JsonResponse(result)


def tag_search(request, search_str):
    try:
        tag_list = ThreadController(search_str, 'tag').run()
        result = 1
        message = r'搜索分区成功'
    except Exception:
        tag_list = None
        result = 0
        message = r'搜索分区失败'
    result = {'result': result, 'message': message, 'list': tag_list}
    return JsonResponse(result)
