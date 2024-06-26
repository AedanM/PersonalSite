# Generated by Django 5.0.3 on 2024-04-24 10:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0008_skillsandtools_is_a_program_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="skillsandtools",
            name="Skill_Type",
            field=models.TextField(
                choices=[
                    ("Program", "Program"),
                    ("Tool", "Tool"),
                    ("Language", "Language"),
                ],
                default="Language",
            ),
            preserve_default=False,
        ),
    ]
