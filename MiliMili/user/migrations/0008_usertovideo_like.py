# Generated by Django 4.0.2 on 2022-04-17 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_alter_user_avatar_alter_user_avatar_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToVideo_like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='主体')),
                ('video_id', models.IntegerField(default=0, verbose_name='点赞的视频')),
            ],
        ),
    ]
