# Generated by Django 4.1.7 on 2023-03-20 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0010_messages_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='filemessage',
            field=models.FileField(default=None, null=True, upload_to='chats/files'),
        ),
        migrations.AlterField(
            model_name='messages',
            name='imagemessage',
            field=models.ImageField(default=None, null=True, upload_to='chats/images'),
        ),
    ]
