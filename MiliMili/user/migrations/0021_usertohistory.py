# Generated by Django 4.0.2 on 2022-05-31 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_delete_usertohistory_alter_usertovideo_collect_cnt'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='主体')),
                ('video_id', models.IntegerField(default=0, verbose_name='看过的视频')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'ordering': ['-created_time'],
            },
        ),
    ]
