from django.db import models

from user.models import User


class Message(models.Model):
    title = models.CharField('标题', max_length=32)
    content = models.TextField('评论内容')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    user = models.ForeignKey(User, verbose_name='所属用户', on_delete=models.CASCADE)
    isRead = models.BooleanField("是否已读", default=False)

    def to_dic(self):
        return {
            "title": self.title,
            "content": self.content,
            "created_time": self.created_time,
            "isRead": self.isRead,
        }

    def __str__(self):
        return '站内信' + self.title

    class Meta:
        ordering = ['-created_time']  # 按文章创建日期降序
        db_table = 'message'  # 改变当前模型类对应的表名
        verbose_name = '站内信'
        verbose_name_plural = '站内信列表'

    def read(self):
        self.isRead = True
        self.save(update_fields=['isRead'])
