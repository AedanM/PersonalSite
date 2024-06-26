# Generated by Django 5.0.3 on 2024-04-23 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0002_alter_education_qualification_level_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgrammingLanguage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("LanguageName", models.TextField()),
                (
                    "Proficiency",
                    models.TextField(
                        choices=[
                            ("Proficient", "Proficient"),
                            ("Experienced", "Experienced"),
                            ("Comfortable", "Comfortable"),
                            ("Familar", "Familiar"),
                            ("Beginner", "Beginner"),
                            ("Never Used", "Never Used"),
                        ]
                    ),
                ),
            ],
        ),
    ]
