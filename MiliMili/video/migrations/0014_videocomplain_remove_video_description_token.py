# Generated by Django 4.0.2 on 2022-04-19 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0013_video_description_token_video_title_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoComplain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='标题')),
                ('description', models.TextField(verbose_name='描述')),
            ],
        ),
        migrations.RemoveField(
            model_name='video',
            name='description_token',
        ),
    ]
