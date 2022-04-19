from django.http import JsonResponse
from index.ThreadController import ThreadController


def video_search(request, search_str):
    try:
        video_list = ThreadController(search_str, 'video')
        result = 1
        message = r'搜索视频成功'
    except Exception:
        video_list = None
        result = 0
        message = r'搜索视频失败'
    result = {'result': result, 'message': message, 'list': video_list}
    return JsonResponse(result)


def user_search(request, search_str):
    try:
        user_list = ThreadController(search_str, 'user')
        result = 1
        message = r'搜索用户成功'
    except Exception:
        user_list = None
        result = 0
        message = r'搜索用户失败'
    result = {'result': result, 'message': message, 'list': user_list}
    return JsonResponse(result)


def tag_search(request, search_str):
    try:
        user_list = ThreadController(search_str, 'tag')
        result = 1
        message = r'搜索分区成功'
    except Exception:
        user_list = None
        result = 0
        message = r'搜索分区失败'
    result = {'result': result, 'message': message, 'list': user_list}
    return JsonResponse(result)