# Generated by Django 5.1 on 2024-09-09 10:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("media", "0011_albums"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Albums",
            new_name="Album",
        ),
    ]
