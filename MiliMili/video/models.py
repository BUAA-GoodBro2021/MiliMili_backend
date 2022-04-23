from django.db import models
from user.models import User


class Video(models.Model):
    title = models.CharField('标题', max_length=64)
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

    isAudit = models.IntegerField('状态', default=0)  # 0 - 待审核   1 - 审核通过    2 - 需要人工审核
    need_verify = models.IntegerField('状态', default=0)  # 0 - 正常视频  1 - 投诉过多需要临时下架进行人工检查的视频

    def to_dic(self):
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
            'tag1': self.tag1,
            'tag2': self.tag2,
            'tag3': self.tag3,
            'tag4': self.tag4,
            'tag5': self.tag5,
            'user': self.user.to_dic(),
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'isAudit': self.isAudit,
            'need_verify': self.need_verify,
        }

    def __str__(self):
        return '视频' + self.title

    class Meta:
        ordering = ['-updated_time']  # 按文章创建日期降序
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
    video = models.ForeignKey(Video, verbose_name='所属文章', on_delete=models.CASCADE)

    reply_comment_id = models.IntegerField("回复评论编号", default=0)
    reply_username = models.CharField('回复评论用户名', max_length=30, default="null")

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
            'content': self.content,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'video_id': self.video.id,
            'reply_comment_id': self.reply_comment_id,
            'reply_username': self.reply_username,
        }


# 视频投诉
class VideoComplain(models.Model):
    title = models.CharField('标题', max_length=64)
    description = models.TextField('描述')
    user_id = models.IntegerField(verbose_name='投诉人员编号', default=0)
    video = models.ForeignKey(Video, verbose_name='所属视频', on_delete=models.CASCADE, default=None)

    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'video': self.video.to_dic(),
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

    def to_dic(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'isPrivate': self.isPrivate,
        }


class FavoriteToVideo(models.Model):
    favorite_id = models.IntegerField(verbose_name='收藏夹编号', default=0)
    video_id = models.IntegerField(verbose_name='视频编号', default=0)


