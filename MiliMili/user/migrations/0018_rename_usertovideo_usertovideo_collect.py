# Generated by Django 4.0.2 on 2022-05-31 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_alter_user_avatar_url'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserToVideo',
            new_name='UserToVideo_collect',
        ),
    ]