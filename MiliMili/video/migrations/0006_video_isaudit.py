# Generated by Django 4.0.2 on 2022-04-14 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0005_alter_video_avatar_alter_video_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='isAudit',
            field=models.IntegerField(default=0, verbose_name='状态'),
        ),
    ]
