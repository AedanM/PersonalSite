# Generated by Django 5.0.3 on 2024-04-23 16:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0005_rename_languagename_skillsandtools_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="skillsandtools",
            name="IsLang",
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
