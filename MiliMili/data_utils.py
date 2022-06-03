import threading
import time

from index.ThreadController import ThreadController
from user.models import UserToSearchHistory
from video.models import UserToHistory, Video, Zone


# 搜索缓存
class SearchData:
    search_thread = {'video': {},
                     'user': {}}

    def __init__(self, search_str, element):
        self.element = element
        thread_dict = self.search_thread[element]
        self.search_str = search_str
        if search_str not in thread_dict.keys():
            thread = SearchThreading(search_str, element)
            thread_dict[search_str] = thread
            thread.start()
        elif not thread_dict[search_str].is_alive():
            thread = thread_dict[search_str]
            thread = SearchThreading(search_str, element, thread.element_list, True)
            thread_dict[search_str] = thread
            thread.start()

    def get_data(self):
        thread = self.search_thread[self.element][self.search_str]
        while True:
            if thread.flag:
                return {'element_list': thread.element_list}
            time.sleep(1)


# 缓存线程
class SearchThreading(threading.Thread):
    def __init__(self, search_str, element, element_list=None, flag=False):
        threading.Thread.__init__(self)
        if not flag:
            self.element_list = []
            self.flag = False
        else:
            self.element_list = element_list
            self.flag = True
        self.search_str = search_str
        self.element = element

    def run(self):
        self.element_list = ThreadController(self.search_str, self.element).run()
        self.flag = True


# 主页信息缓存
class IndexData:
    id_thread = {}

    def __init__(self, user_id):
        self.user_id = user_id
        if user_id not in self.id_thread.keys():
            thread = IndexThreading(user_id)
            self.id_thread[user_id] = thread
            thread.start()
        elif not self.id_thread[user_id].is_alive():
            thread = self.id_thread[user_id]
            thread = IndexThreading(user_id, thread.recommend_list,
                                    thread.search_history_list, thread.zone_list,
                                    thread.zone_video_list, True)
            self.id_thread[user_id] = thread
            thread.start()

    def get_data(self):
        thread = self.id_thread[self.user_id]
        while True:
            if thread.flag:
                return {'recommend_list': thread.recommend_list,
                        'search_history_list': thread.search_history_list,
                        'zone_list': thread.zone_list,
                        'zone_video_list': thread.zone_video_list}
            time.sleep(1)


# 主页多线程
class IndexThreading(threading.Thread):
    def __init__(self, user_id, recommend_list=None,
                 search_history_list=None, zone_list=None,
                 zone_video_list=None, flag=False):
        threading.Thread.__init__(self)
        if not flag:
            self.recommend_list = []
            self.search_history_list = []
            self.zone_list = []
            self.zone_video_list = []
            self.flag = False
        else:
            self.recommend_list = recommend_list
            self.search_history_list = search_history_list
            self.zone_list = zone_list
            self.zone_video_list = zone_video_list
            self.flag = True
        self.user_id = user_id

    def run(self):
        cnt = 0
        # 每个线程存活半小时
        while cnt < 6:
            cnt += 1
            history_list = list(UserToHistory.objects.filter(user_id=self.user_id).values())[0:20]
            tag_dict = {}
            for history_info in history_list:
                video_info = Video.objects.get(id=history_info.get('video_id', ''))
                if video_info is not None:
                    for i in range(1, 6):
                        tag = eval('video_info.tag' + str(i))
                        if tag != '':
                            if tag not in tag_dict.keys():
                                tag_dict[tag] = 1
                            else:
                                tag_dict[tag] += 1
            zone_list = list(Zone.objects.all().values())
            try:
                recommend_list = ThreadController(None, 'recommend', tag_dict).run()[:6]
            except Exception as e:
                recommend_list = []
            try:
                zone_video_list = []
                for i in zone_list:
                    zone_video_list.append({'id': i['id']})
                    zone_video_list[i['id'] - 1]['recommend_list'] = ThreadController(i['zone'], 'recommend',
                                                                                      tag_dict).run()[:8]
                    zone_video_list[i['id'] - 1]['rank_list'] = ThreadController(i['zone'], 'zone').run()[:10]
            except Exception as e:
                zone_video_list = []
                for i in zone_list:
                    zone_video_list.append({'id': i['id']})
                    zone_video_list[i['id'] - 1]['recommend_list'] = []
                    zone_video_list[i['id'] - 1]['rank_list'] = []
            search_history_list = list(UserToSearchHistory.objects.filter(user_id=self.user_id).values())
            search_history_list = sorted(search_history_list, key=lambda x: -x.get('created_time').timestamp())[:8]
            self.recommend_list = recommend_list
            self.search_history_list = search_history_list
            self.zone_list = zone_list
            self.zone_video_list = zone_video_list
            self.flag = True
            time.sleep(300)
