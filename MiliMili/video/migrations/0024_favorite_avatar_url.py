# Generated by Django 4.0.2 on 2022-05-14 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0023_videocomment_islike'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='avatar_url',
            field=models.CharField(default='https://global-1309504341.cos.ap-beijing.myqcloud.com/default-favorite.jpg', max_length=128, verbose_name='封面路径'),
        ),
    ]
