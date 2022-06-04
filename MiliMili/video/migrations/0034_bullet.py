# Generated by Django 4.0.2 on 2022-06-04 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_usertocomment_like_root_id'),
        ('video', '0033_videocomment_reply_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bullet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='', verbose_name='弹幕内容')),
                ('approach_time', models.CharField(default='', max_length=64, verbose_name='分区名称')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='所属用户')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='video.video', verbose_name='所属视频')),
            ],
        ),
    ]
