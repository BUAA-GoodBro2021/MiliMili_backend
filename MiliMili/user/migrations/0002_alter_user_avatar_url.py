# Generated by Django 4.0.3 on 2022-04-08 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar_url',
            field=models.FileField(default='avatar/', upload_to='avatar', verbose_name='用户头像'),
        ),
    ]
