# Generated by Django 4.0.4 on 2022-04-24 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0019_delete_auditedtag_delete_unauditedtag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=64, verbose_name='标签集合')),
                ('count', models.IntegerField(default=0, verbose_name='选用此标签的视频数量')),
            ],
        ),
    ]
