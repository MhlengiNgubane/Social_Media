# Generated by Django 4.2.16 on 2024-10-15 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0004_post_tags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="tags",
        ),
    ]
