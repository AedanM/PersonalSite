# Generated by Django 5.0.3 on 2024-04-16 15:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resume", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="education",
            name="Qualification_Level",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="employment",
            name="Responsibilities",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="employment",
            name="Skills_Gained",
            field=models.TextField(blank=True, default=""),
        ),
    ]
