# Generated by Django 4.2.16 on 2024-10-17 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0005_remove_post_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hashtag",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
