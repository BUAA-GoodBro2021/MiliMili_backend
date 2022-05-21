from django.db import models

from user.models import User


class Message(models.Model):
    title = models.CharField('标题', max_length=32)
    content = models.TextField('评论内容')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    user = models.ForeignKey(User, verbose_name='所属用户', on_delete=models.CASCADE)
    isRead = models.BooleanField("是否已读", default=False)
    from_id = models.IntegerField('发送者id', default=1)
    from_type = models.IntegerField('分类', default=0)  # 0 - 系统通知 1 - 评论回复我的 2 - 收到的赞 3 - 收藏 4 - 我的消息(私信) 5 - 新增粉丝

    def to_dic(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_time": self.created_time,
            "isRead": self.isRead,
            "from_id": self.from_id,
            "from_type": self.from_type,
            'from_user': User.objects.get(id=self.from_id).to_dic(),
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
