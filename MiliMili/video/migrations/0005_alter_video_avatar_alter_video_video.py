# Generated by Django 4.0.3 on 2022-04-10 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0004_alter_video_avatar_alter_video_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='avatar',
            field=models.FileField(default='', upload_to='', verbose_name='封面'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(default='', upload_to='', verbose_name='视频'),
        ),
    ]