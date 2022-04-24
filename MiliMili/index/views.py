import datetime
import requests
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
            video_list = sorted(video_list, key=lambda x: -x.get('updated_time').timestamp())
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


def get_ip_address(request):
    # coding=UTF-8
    res = ''
    host = 'https://ips.market.alicloudapi.com'
    path = '/iplocaltion'
    method = 'GET'
    appcode = '1437a6fc99dc4078bfe01338d7132c2c'  # 开通服务后 买家中心-查看AppCode
    querys = "ip=" + request.META['REMOTE_ADDR']
    print(querys)
    bodys = {}
    url = host + path + '?' + querys
    header = {"Authorization": 'APPCODE ' + appcode}
    try:
        res = requests.get(url, headers=header)
    except:
        print("URL错误")
        exit()
    httpStatusCode = res.status_code

    if httpStatusCode == 200:
        print("正常请求计费(其他均不计费)")
        print(res.text)
        return JsonResponse(res.text)
    else:
        httpReason = res.headers['X-Ca-Error-Message']
        if httpStatusCode == 400 and httpReason == 'Invalid Param Location':
            print("参数错误")
            return JsonResponse({"result": 0, "message": "参数错误"})
        elif httpStatusCode == 400 and httpReason == 'Invalid AppCode':
            print("AppCode错误")
            return JsonResponse({"result": 0, "message": "AppCode错误"})
        elif httpStatusCode == 400 and httpReason == 'Invalid Url':
            print("请求的 Method、Path 或者环境错误")
            return JsonResponse({"result": 0, "message": "请求的 Method、Path 或者环境错误"})
        elif httpStatusCode == 403 and httpReason == 'Unauthorized':
            print("服务未被授权（或URL和Path不正确）")
            return JsonResponse({"result": 0, "message": "服务未被授权（或URL和Path不正确）"})
        elif httpStatusCode == 403 and httpReason == 'Quota Exhausted':
            print("套餐包次数用完")
            return JsonResponse({"result": 0, "message": "套餐包次数用完"})
        elif httpStatusCode == 403 and httpReason == 'Api Market Subscription quota exhausted':
            print("套餐包次数用完，请续购套餐")
            return JsonResponse({"result": 0, "message": "套餐包次数用完，请续购套餐"})
        elif httpStatusCode == 500:
            print("API网关错误")
            return JsonResponse({"result": 0, "message": "API网关错误"})
        else:
            print("参数名错误 或 其他错误")
            print(httpStatusCode)
            print(httpReason)
            return JsonResponse({"result": 0, "message": "参数名错误 或 其他错误"})
