# Generated by Django 5.0.3 on 2024-04-24 10:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0007_rename_islang_skillsandtools_is_a_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="skillsandtools",
            name="Is_a_Program",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="skillsandtools",
            name="Proficiency",
            field=models.TextField(
                choices=[
                    ("Proficient", "Proficient"),
                    ("Experienced", "Experienced"),
                    ("Comfortable", "Comfortable"),
                    ("Familiar", "Familiar"),
                    ("Beginner", "Beginner"),
                    ("Never Used", "Never Used"),
                ]
            ),
        ),
    ]
