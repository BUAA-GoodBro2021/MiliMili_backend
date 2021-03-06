# Generated by Django 4.0.2 on 2022-04-19 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0015_videocomplain_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videocomplain',
            name='user',
        ),
        migrations.AddField(
            model_name='videocomplain',
            name='user_id',
            field=models.IntegerField(default=0, verbose_name='投诉人员编号'),
        ),
        migrations.AddField(
            model_name='videocomplain',
            name='video',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='video.video', verbose_name='所属视频'),
        ),
    ]
