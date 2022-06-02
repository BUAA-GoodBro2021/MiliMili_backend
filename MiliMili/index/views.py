import random

import jwt
import requests

from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from MiliMili.settings import SECRET_KEY
from index.ThreadController import ThreadController
from key import *
from sending.views import not_read
from user.models import *
from video.models import Video, Zone, UserToHistory
from video.views import is_follow


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

        # 是否是登录状态
        JWT = request.POST.get('JWT', '')
        if JWT == '' or JWT is None:
            result = {'result': result, 'message': message, 'not_read': -1, 'list': video_list}
            return JsonResponse(result)
        else:
            JWT = request.POST.get('JWT', '')
            try:
                token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': r"JWT错误，请先登录!"}
                return JsonResponse(result)
            result = {'result': result, 'message': message, 'not_read': not_read(user_id), 'list': video_list}
            return JsonResponse(result)
    else:
        video_list = None
        result = 0
        message = r'搜索视频失败'
        result = {'result': result, 'message': message, 'not_read': -1, 'list': video_list}
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
        # 是否是登录状态
        JWT = request.POST.get('JWT', '')
        if JWT == '' or JWT is None:
            result = {'result': result, 'message': message, 'not_read': -1, 'list': user_list}
            return JsonResponse(result)
        else:
            JWT = request.POST.get('JWT', '')
            try:
                token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': r"JWT错误，请先登录!"}
                return JsonResponse(result)
            for user in user_list:
                if is_follow(user_id, user.get('id')):
                    user['is_follow'] = True
                else:
                    user['is_follow'] = False
            result = {'result': result, 'message': message, 'not_read': not_read(user_id), 'list': user_list}
            return JsonResponse(result)

    else:
        user_list = None
        result = 0
        message = r'搜索用户失败'
        result = {'result': result, 'message': message, 'not_read': -1, 'list': user_list}
        return JsonResponse(result)


def zone_search(request, zone):
    if request.method == 'POST':
        try:
            zone = Zone.objects.get(id=zone)
            zone_list = ThreadController(zone.zone, 'zone').run()
            result = 1
            message = r'搜索分区成功'
        except Exception:
            zone_list = None
            result = 0
            message = r'搜索分区失败'

        # 是否是登录状态
        JWT = request.POST.get('JWT', '')
        if JWT == '' or JWT is None:
            result = {'result': result, 'message': message, 'not_read': -1,
                      'random_list': random.sample(zone_list[0], min(5, len(zone_list[0]))),
                      'all_list': zone_list[0],
                      'view_rank_list': zone_list[0],
                      'like_rank_list': zone_list[1],
                      'collect_rank_list': zone_list[2]}
            return JsonResponse(result)
        else:
            JWT = request.POST.get('JWT', '')
            try:
                token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': r"JWT错误，请先登录!"}
                return JsonResponse(result)
            result = {'result': result, 'message': message, 'not_read': not_read(user_id),
                      'random_list': random.sample(zone_list[0], min(5, len(zone_list[0]))),
                      'all_list': zone_list[0],
                      'view_rank_list': zone_list[0],
                      'like_rank_list': zone_list[1],
                      'collect_rank_list': zone_list[2]}
            return JsonResponse(result)

    else:
        zone_list = None
        result = 0
        message = r'搜索分区失败'
        result = {'result': result, 'message': message, 'not_read': -1, 'list': zone_list}
        JsonResponse(result)


@cache_page(60 * 5)
def index_message(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, SECRET_KEY, algorithms=['HS256'])
            user_id = token.get('user_id', '')
        except Exception:
            user_id = -1
        history_list = list(UserToHistory.objects.filter(user_id=user_id).values())[0:20]
        tag_dict = {}
        for history_info in history_list:
            video_info = Video.objects.get(id=history_info.get('video_id', ''))
            if video_info is not None:
                for i in range(1, 6):
                    tag = ''
                    if i == 1:
                        tag = video_info.tag1
                    elif i == 2:
                        tag = video_info.tag2
                    elif i == 3:
                        tag = video_info.tag3
                    elif i == 4:
                        tag = video_info.tag4
                    elif i == 5:
                        tag = video_info.tag5
                    if tag != '':
                        if tag not in tag_dict.keys():
                            tag_dict[tag] = 1
                        else:
                            tag_dict[tag] += 1
        zone_list = list(Zone.objects.all().values())
        try:
            recommend_list = ThreadController(None, 'recommend', tag_dict).run()[:6]
            result = 1
            message = r'推荐成功'
        except Exception as e:
            print(e)
            recommend_list = None
            result = 0
            message = r'推荐失败'
        try:
            zone_video_list = []
            for i in zone_list:
                zone_video_list.append({'id': i['id']})
                zone_video_list[i['id'] - 1]['recommend_list'] = ThreadController(i['zone'], 'recommend',
                                                                                  tag_dict).run()[:8]
                zone_video_list[i['id'] - 1]['rank_list'] = ThreadController(i['zone'], 'zone').run()[:10]
        except Exception as e:
            print(e)
            zone_video_list = None
            result = 0
            message = r'推荐失败'
        search_history_list = list(UserToSearchHistory.objects.filter(user_id=user_id).values())
        search_history_list = sorted(search_history_list, key=lambda x: -x.get('created_time').timestamp())[:8]

        result = {'result': result, 'message': message, "not_read": not_read(user_id), 'recommend_list': recommend_list,
                  'search_history_list': search_history_list, 'zone_list': zone_list,
                  'zone_video_list': zone_video_list}
        return JsonResponse(result)


def history_view(request):
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
        history_filter = UserToHistory.objects.filter(user_id=user_id)
        history_list = [x.to_dic() for x in history_filter]
        result = {'result': 1, 'message': r"获取详情列表成功！", "not_read": not_read(user_id), "history": history_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def get_ip_address(request):
    # coding=UTF-8
    res = ''
    host = 'https://ips.market.alicloudapi.com'
    path = '/iplocaltion'
    appcode = aliyun_appcode
    querys = "ip=" + request.META['REMOTE_ADDR']
    print(querys)
    url = host + path + '?' + querys
    header = {"Authorization": 'APPCODE ' + appcode}
    try:
        res = requests.get(url, headers=header)
    except Exception:
        print("URL错误")
        exit()
    httpStatusCode = res.status_code

    if httpStatusCode == 200:
        print("正常请求计费(其他均不计费)")
        print(res.text)
        return JsonResponse(eval(res.text))
        # return HttpResponse(res.text)
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
