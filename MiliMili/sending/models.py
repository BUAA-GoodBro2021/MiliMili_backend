from django.db import models


# Create your models here.
class Email_code(models.Model):
    email_code = models.CharField(max_length=100)

    class Meta:
        db_table = 'email_code'  # 改变当前模型类对应的表名
        verbose_name = '验证码'
        verbose_name_plural = verbose_name
