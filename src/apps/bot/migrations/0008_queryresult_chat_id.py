# Generated by Django 4.1 on 2022-08-29 14:31
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0007_queryresult_message_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="queryresult",
            name="chat_id",
            field=models.IntegerField(default=0, help_text="chat id"),
            preserve_default=False,
        ),
    ]
