from django.http import JsonResponse
from index.ThreadController import ThreadController
from user.models import UserToHistory
from video.models import Video


def video_search(request):
    if request.method == 'POST':
        search_str = request.POST.get('search_str', '')
        try:
            video_list = ThreadController(search_str, 'video').run()
            result = 1
            message = r'搜索视频成功'
        except Exception:
            video_list = None
            result = 0
            message = r'搜索视频失败'
        order = request.POST.get('order', '')
        if order == 'default' or video_list is None:
            pass
        elif order == 'time':
            video_list = sorted(video_list, key=lambda x: -x.get('updated_time'))
        elif order == 'view':
            video_list = sorted(video_list, key=lambda x: -x.get('view_num'))
    else:
        video_list = None
        result = 0
        message = r'搜索视频失败'
    result = {'result': result, 'message': message, 'list': video_list}
    return JsonResponse(result)


def user_search(request):
    if request.method == 'POST':

        search_str = request.POST.get('search_str', '')
        try:
            user_list = ThreadController(search_str, 'user').run()
            result = 1
            message = r'搜索用户成功'
        except Exception:
            user_list = None
            result = 0
            message = r'搜索用户失败'
        order = request.POST.get('order', '')
        if order == 'default' or user_list is None:
            pass
        elif order == 'fan':
            user_list = sorted(user_list, key=lambda x: -x.get('fan_num'))
        else:
            pass
    else:
        user_list = None
        result = 0
        message = r'搜索用户失败'
    result = {'result': result, 'message': message, 'list': user_list}
    return JsonResponse(result)


def zone_search(request, zone):
    try:
        zone_list = ThreadController(zone, 'zone').run()
        result = 1
        message = r'搜索分区成功'
    except Exception:
        zone_list = None
        result = 0
        message = r'搜索分区失败'
    result = {'result': result, 'message': message, 'list': zone_list}
    return JsonResponse(result)


def recommend_video(request):
    history_list = list(UserToHistory.objects.all().values())[0:20]
    tag_dict = {}
    for history_info in history_list:
        video_info = Video.objects.get(id=history_info.get('video_id', ''))
        if video_info is not None:
            for i in range(1, 6):
                tag = video_info.get('tag' + str(i))
                if tag != '':
                    if tag not in tag_dict.keys():
                        tag_dict[tag] = 1
                    else:
                        tag_dict[tag] += 1
    try:
        recommend_list = ThreadController(tag_dict, 'recommend').run()
        result = 1
        message = r'推荐成功'
    except Exception:
        recommend_list = None
        result = 0
        message = r'推荐失败'
    result = {'result': result, 'message': message, 'list': recommend_list}
    return JsonResponse(result)
