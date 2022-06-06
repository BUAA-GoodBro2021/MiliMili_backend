from django.db import models

from key import default_favorite_url
from user.models import User


class Video(models.Model):
    title = models.CharField('标题', max_length=256)
    description = models.TextField('描述')
    video = models.FileField('视频', upload_to='', default='')
    avatar = models.FileField('封面', upload_to='', default='')
    video_url = models.CharField('视频路径', max_length=128, default='')
    avatar_url = models.CharField('封面路径', max_length=128, default='')

    like_num = models.IntegerField(verbose_name='点赞数', default=0)
    collect_num = models.IntegerField(verbose_name='收藏数', default=0)
    view_num = models.IntegerField('浏览量', default=0)
    zone = models.CharField('专区', max_length=32, default='')
    tag1 = models.CharField('标签1', max_length=32, default='')
    tag2 = models.CharField('标签2', max_length=32, default='')
    tag3 = models.CharField('标签3', max_length=32, default='')
    tag4 = models.CharField('标签4', max_length=32, default='')
    tag5 = models.CharField('标签5', max_length=32, default='')

    user = models.ForeignKey(User, verbose_name='所属用户', on_delete=models.CASCADE)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    isAudit = models.IntegerField('状态', default=0)  # 0 - 待审核   1 - 审核通过    2 - 需要人工审核   3 - 被管理员手动改为审核

    def to_dic(self):
        tag_list = []
        if self.tag1 != '':
            tag_list.append(self.tag1)
        if self.tag2 != '':
            tag_list.append(self.tag2)
        if self.tag3 != '':
            tag_list.append(self.tag3)
        if self.tag4 != '':
            tag_list.append(self.tag4)
        if self.tag5 != '':
            tag_list.append(self.tag5)
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'avatar_url': self.avatar_url,
            'like_num': self.like_num,
            'collect_num': self.collect_num,
            'view_num': self.view_num,
            'zone': self.zone,
            'tag_list': tag_list,
            'user': self.user.to_simple_dic(),
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'isAudit': self.isAudit,
            'bullet': [x.to_dic() for x in self.bullet_set.all()]
        }

    def to_simple_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'avatar_url': self.avatar_url,
            'view_num': self.view_num,
            'user': self.user.to_simple_dic(),
            'created_time': self.created_time,
        }

    def __str__(self):
        return '视频' + self.title

    class Meta:
        ordering = ['-updated_time']  # 按视频创建日期降序
        db_table = 'video'  # 改变当前模型类对应的表名
        verbose_name = '视频'
        verbose_name_plural = '视频列表'

    # 更新浏览量
    def add_view(self):
        self.view_num += 1
        self.save(update_fields=['view_num'])

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


# 视频评论
class VideoComment(models.Model):
    username = models.CharField('用户名', max_length=30)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    content = models.TextField('评论内容')
    video = models.ForeignKey(Video, verbose_name='所属视频', on_delete=models.CASCADE)

    reply_comment_id = models.IntegerField("回复评论编号", default=0)
    reply_username = models.CharField('回复评论用户名', max_length=30, default="null")
    reply_user_id = models.IntegerField('回复评论用户id', default=0)
    root_id = models.IntegerField("根编号", default=0)
    user_id = models.IntegerField("所属用户号", default=0)

    like_num = models.IntegerField(verbose_name='点赞数', default=0)
    is_like = models.IntegerField(verbose_name='是否已点赞', default=0)
    is_own = models.IntegerField(verbose_name='是否是可修改的', default=0)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['-created_time']
        verbose_name = '评论'  # 指定后台显示模型名称
        verbose_name_plural = '评论列表'  # 指定后台显示模型复数名称
        db_table = "comment"  # 数据库表名

    def to_dic(self):
        return {
            'id': self.id,
            'username': self.username,
            'user_id': self.user_id,
            'avatar_url': User.objects.get(id=self.user_id).avatar_url,
            'content': self.content,
            'like_num': self.like_num,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'video_id': self.video.id,
            'root_id': self.root_id,
            'reply_comment_id': self.reply_comment_id,
            'reply_username': self.reply_username,
            'reply_user_id': self.reply_user_id,
            'is_like': self.is_like,
            'is_own': self.is_own,
        }

    # 评论获得点赞
    def add_like(self):
        self.like_num += 1
        self.save(update_fields=['like_num'])

    # 评论取消点赞
    def del_like(self):
        if self.like_num > 0:
            self.like_num -= 1
            self.save(update_fields=['like_num'])


# 视频投诉
class VideoComplain(models.Model):
    title = models.CharField('标题', max_length=64)
    description = models.TextField('描述')
    user_id = models.IntegerField(verbose_name='投诉人员编号', default=0)
    video = models.ForeignKey(Video, verbose_name='所属视频', on_delete=models.CASCADE, default=None)
    verify_result = models.IntegerField(verbose_name='投诉结果', default=0)  # 0 - 正处于投诉状态，  1 - 投诉不成功   2 - 投诉成功

    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'verify_result': self.verify_result,
            'video': self.video.to_simple_dic(),
        }


# 腾讯云自动审核
class JobToVideo(models.Model):
    job_id = models.CharField(verbose_name='审核编号', max_length=128, default='')
    video_id = models.IntegerField(verbose_name='视频编号', default=0)


# 收藏夹
class Favorite(models.Model):
    title = models.CharField('默认收藏夹', max_length=64)
    description = models.TextField('描述')
    isPrivate = models.IntegerField("是否为私有", default=0)  # 0 - 公开    1 - 私有
    user = models.ForeignKey(User, verbose_name='所属用户', on_delete=models.CASCADE)
    avatar_url = models.CharField('封面路径', max_length=128, default=default_favorite_url)

    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'avatar_url': self.avatar_url,
            'isPrivate': self.isPrivate,
        }

    def to_simple_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'avatar_url': self.avatar_url,
        }


class FavoriteToVideo(models.Model):
    favorite_id = models.IntegerField(verbose_name='收藏夹编号', default=0)
    video_id = models.IntegerField(verbose_name='视频编号', default=0)


class Tag(models.Model):
    tag = models.CharField(verbose_name='标签集合', max_length=64)
    count = models.IntegerField(verbose_name='选用此标签的视频数量', default=0)


class Zone(models.Model):
    zone = models.CharField(verbose_name='分区名称', max_length=64)


# 查看用户历史记录
class UserToHistory(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    video_id = models.IntegerField(verbose_name='看过的视频', default=0)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_time']

    def to_dic(self):
        return {
            'video': Video.objects.get(id=self.video_id).to_simple_dic()
        }


class Bullet(models.Model):
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    video = models.ForeignKey(Video, verbose_name='所属视频', on_delete=models.CASCADE)
    bullet_id = models.IntegerField(verbose_name='弹幕id', default=1)
    start = models.CharField(verbose_name='到达时间', max_length=16, default='')
    txt = models.TextField('弹幕内容', default='')
    style_color = models.CharField(verbose_name='弹幕颜色', max_length=16, default='')
    style_fontSize = models.CharField(verbose_name='弹幕字体', max_length=16, default='')
    mode = models.CharField(verbose_name='弹幕显示位置', max_length=16, default='')

    def to_dic(self):
        return {
            'duration': 15000,  # 弹幕持续显示时间,毫秒(最低为5000毫秒)
            'id': self.bullet_id,  # 弹幕id，需唯一
            'start': self.start,  # 弹幕出现时间，毫秒
            'prior': True,  # 该条弹幕优先显示，默认false
            'color': True,  # 该条弹幕为彩色弹幕，默认false
            'txt': self.txt,  # 弹幕文字内容
            'style': {  # 弹幕自定义样式
                'color': self.style_color,
                'fontSize': self.style_fontSize,
                'border': 'solid 1px #ff9500',
                'borderRadius': '50px',
                'padding': '5px 11px',
                'backgroundColor': 'rgba(255, 255, 255, 0.1)'
            },
            'mode': self.mode,  # 显示模式，top顶部居中，bottom底部居中，scroll滚动，默认为scroll
            'created_time': self.created_time
        }

    class Meta:
        ordering = ['bullet_id']
