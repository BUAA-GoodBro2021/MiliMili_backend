# Generated by Django 4.0.2 on 2022-05-14 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0021_videocomplain_verify_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='videocomment',
            name='like_num',
            field=models.IntegerField(default=0, verbose_name='点赞数'),
        ),
    ]
