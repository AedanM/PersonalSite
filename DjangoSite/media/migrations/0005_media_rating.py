# Generated by Django 5.0.3 on 2024-04-11 18:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("media", "0004_comic_novel_delete_book"),
    ]

    operations = [
        migrations.AddField(
            model_name="media",
            name="Rating",
            field=models.IntegerField(default=0),
        ),
    ]
