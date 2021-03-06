# Generated by Django 4.0.2 on 2022-04-17 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_user_collect_num'),
        ('video', '0009_video_need_verify'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='默认收藏夹')),
                ('description', models.TextField(verbose_name='描述')),
                ('isPrivate', models.BooleanField(default=False, verbose_name='是否为私有')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='所属用户')),
            ],
        ),
    ]
