# Generated by Django 5.1.2 on 2024-11-05 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("media", "0013_alter_media_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="Genre_Tags",
            field=models.CharField(max_length=200),
        ),
    ]
