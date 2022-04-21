import math
import random
import threading
import jieba
from django.db.models import Q

from video.models import Video
from user.models import User


class ThreadController:
    def __init__(self, search, element, thread_num=10):
        """
        :param search: the searched string or dict ({tag: count})
        :param element: the type of search (video, user, tag)
        :param thread_num: the number of threading
        """
        self.search_token_list = list(jieba.cut_for_search(search))
        self.search = search
        if element == 'video':
            self.element_list = list(Video.objects.filter(isAudit=1, need_verify=0).values())
        elif element == 'user':
            self.element_list = list(User.objects.all().values())
        elif element == 'zone':
            self.element_list = list(Video.objects.filter(isAudit=1, need_verify=0, zone=search).values())
            print(self.element_list)
        elif element == 'recommend':
            key = search.keys()
            self.element_list = list(Video.objects.filter((Q(tag1__in=key) | Q(tag2__in=key) |
                                     Q(tag3__in=key) | Q(tag4__in=key) |
                                     Q(tag5__in=key)), isAudit=1, need_verify=0).values())
        else:
            self.element_list = []
        block_size = math.floor(len(self.element_list) / thread_num)
        if block_size == 0:
            thread_num = 1
        distribution_list = [[block_size * i, block_size * (i + 1)] for i in range(thread_num)]
        distribution_list[thread_num - 1][1] = len(self.element_list)
        self.element = element
        self.threads = [self.Threading(element, self.search, self.search_token_list,
                                       self.element_list[distribution_list[i][0]:distribution_list[i][1]])
                        for i in range(thread_num)]

    def run(self):
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()
        if self.element == 'video':
            result = sorted(self.Threading.ranked_element_list, key=lambda x: (x.get('distance'), -x.get('view_num'),
                                                                               -x.get('like_num')))
        elif self.element == 'user':
            result = sorted(self.Threading.ranked_element_list, key=lambda x: (x.get('distance'), -x.get('fan_num'),
                                                                               -x.get('like_num')))
        elif self.element == 'zone':
            result = sorted(self.element_list, key=lambda x: (-x.get('view_num'), -x.get('like_num')))
        elif self.element == 'recommend':
            result = sorted(self.Threading.ranked_element_list, key=lambda x: (x.get('distance'), -x.get('view_num'),
                                                                               -x.get('like_num')))[0:20]
            count = min(len(result), 8)
            result = random.sample(result, count)
        else:
            result = []
        self.Threading.ranked_element_list = []
        return result

    class Threading(threading.Thread):
        ranked_element_list = []

        def __init__(self, element, search, search_token_list, element_list):
            threading.Thread.__init__(self)
            self.search = search
            self.element = element
            self.search_token_list = search_token_list
            self.element_list = element_list

        @staticmethod
        def find_index(s1, s2):
            """
            :param s1: parent str
            :param s2: child str
            :return: the index list where s2 exists in s1
            """
            index = 0
            index_list = []
            hit = 0
            while True:
                index = s1.find(s2, index)
                if not (0 <= index < len(s2)):
                    break
                hit = 1
                index_list.append(index)
                index += 1
            return hit, index_list

        @staticmethod
        def find_change(s1, s2):
            """
            :param s1: parent str
            :param s2: child str
            :return: find whether s1 can match s2
            """
            n = len(s1)
            m = len(s2)
            dp = [[0] * (m + 1) for _ in range(n + 1)]
            index_list = []
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    else:
                        dp[i][j] = max(dp[i][j - 1], dp[i - 1][j])
            step = dp[-1][-1]
            for i in range(n, 0, -1):
                for j in range(m, 0, -1):
                    if dp[i][j] == step and dp[i][j - 1] == dp[i - 1][j] == dp[i - 1][j - 1] == step - 1:
                        step -= 1
                        index_list.append([i - 1, i])
                        m = j
                        break

            return index_list, dp[-1][-1]

        def run(self):
            if self.element == 'video':
                for video_info in self.element_list:
                    index_list = []
                    hit_count = 0
                    for token in self.search_token_list:
                        is_hit, index = self.find_index(video_info.get('title'), token)
                        index_list += index
                        hit_count += is_hit
                    video_info['distance'] = math.fabs(hit_count - len(self.search_token_list))
                    if hit_count != 0:
                        video_info['index_list'] = index_list
                        self.ranked_element_list.append(video_info)
            elif self.element == 'user':
                for user_info in self.element_list:
                    index_list, public_strlen = self.find_change(user_info.get('username'), self.search)
                    user_info['distance'] = len(self.search) + len(user_info.get('username')) - 2 * public_strlen
                    if user_info['distance'] < 5:
                        user_info['index_list'] = index_list
                        self.ranked_element_list.append(user_info)
            elif self.element == 'recommend':
                for video_info in self.element_list:
                    score = 0
                    for i in range(1, 6):
                        score += self.search.get(video_info.get('tag' + str(i)), 0)
                    video_info['distance'] = 100 - score
                self.ranked_element_list += self.element_list
            else:
                pass
