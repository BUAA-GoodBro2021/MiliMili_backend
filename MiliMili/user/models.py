from django.db import models


class User(models.Model):
    username = models.CharField('用户名', max_length=30)
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()
    video_num = models.IntegerField(verbose_name='视频数', default=0)
    like_num = models.IntegerField(verbose_name='收获的点赞数', default=0)
    collect_num = models.IntegerField(verbose_name='收获的收藏数', default=0)
    favorite_num = models.IntegerField(verbose_name='收藏夹数', default=0)
    fan_num = models.IntegerField(verbose_name='粉丝数', default=0)
    follow_num = models.IntegerField(verbose_name='关注数', default=0)
    avatar_url = models.CharField('用户头像路径', max_length=128, default='https://global-1309504341.cos.ap-beijing'
                                                                    '.myqcloud.com/default.jpg')
    avatar = models.FileField('用户头像', upload_to='')
    isActive = models.BooleanField('是否有效', default=False)
    isSuperAdmin = models.BooleanField('是否为超级管理员', default=False)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    complain_time = models.DecimalField('投诉时间', max_digits=12, decimal_places=2,default=0.0)

    def to_dic(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "video_num": self.video_num,
            "like_num": self.like_num,
            "collect_num": self.collect_num,
            'favorite_num': self.favorite_num,
            "fan_num": self.fan_num,
            "follow_num": self.follow_num,
            "avatar_url": self.avatar_url,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "isSuperAdmin": self.isSuperAdmin,
        }

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'  # 改变当前模型类对应的表名
        verbose_name = '网站用户'
        verbose_name_plural = "网站用户列表"

    # 发布视频
    def add_video(self):
        self.video_num += 1
        self.save(update_fields=['video_num'])

    # 删除视频
    def del_video(self):
        if self.video_num > 0:
            self.video_num -= 1
            self.save(update_fields=['video_num'])

    # 视频获得点赞
    def add_like(self):
        self.like_num += 1
        self.save(update_fields=['like_num'])

    # 视频取消点赞
    def del_like(self):
        if self.like_num > 0:
            self.like_num -= 1
            self.save(update_fields=['like_num'])

    # 视频获得收藏
    def add_collect(self):
        self.collect_num += 1
        self.save(update_fields=['collect_num'])

    # 视频取消收藏
    def del_collect(self):
        if self.collect_num > 0:
            self.collect_num -= 1
            self.save(update_fields=['collect_num'])

    # 收获粉丝
    def add_fan(self):
        self.fan_num += 1
        self.save(update_fields=['fan_num'])

    # 减少粉丝
    def del_fan(self):
        if self.fan_num > 0:
            self.fan_num -= 1
            self.save(update_fields=['fan_num'])

    # 添加关注
    def add_follow(self):
        self.follow_num += 1
        self.save(update_fields=['follow_num'])

    # 取消关注
    def del_follow(self):
        if self.follow_num > 0:
            self.follow_num -= 1
            self.save(update_fields=['follow_num'])

    # 添加收藏夹
    def add_favorite(self):
        self.favorite_num += 1
        self.save(update_fields=['favorite_num'])

    # 删除收藏夹
    def del_favorite(self):
        if self.favorite_num > 0:
            self.favorite_num -= 1
            self.save(update_fields=['favorite_num'])


# 查看个人粉丝
class UserToFan(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    fan_id = models.IntegerField(verbose_name='粉丝', default=0)


# 查看个人关注
class UserToFollow(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    follow_id = models.IntegerField(verbose_name='关注的up主', default=0)


# 查看个人收藏的视频
class UserToVideo(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    video_id = models.IntegerField(verbose_name='收藏的视频', default=0)


# 查看个人收藏的视频
class UserToVideo_like(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    video_id = models.IntegerField(verbose_name='点赞的视频', default=0)


# 查看用户历史记录
class UserToHistory(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    video_id = models.IntegerField(verbose_name='看过的视频', default=0)
