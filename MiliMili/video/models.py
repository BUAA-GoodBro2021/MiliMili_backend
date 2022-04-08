from django.db import models

# Create your models here.
from user.models import User


class Video(models.Model):
    title = models.CharField('标题', max_length=64)
    description = models.TextField('描述')
    video_url = models.FileField('视频', upload_to='video', default='video/')
    avatar_url = models.FileField('视频', upload_to='cover', default='cover/')

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
