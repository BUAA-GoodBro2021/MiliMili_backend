# Generated by Django 4.0.2 on 2022-04-19 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_usertosearchhistory'),
        ('video', '0014_videocomplain_remove_video_description_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='videocomplain',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='所属用户'),
        ),
    ]
