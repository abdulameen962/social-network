# Generated by Django 4.1.7 on 2023-03-20 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_chat_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
