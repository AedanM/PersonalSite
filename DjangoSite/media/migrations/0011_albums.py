# Generated by Django 5.1 on 2024-09-09 10:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("media", "0010_alter_tvshow_series_end_alter_tvshow_series_start"),
    ]

    operations = [
        migrations.CreateModel(
            name="Albums",
            fields=[
                (
                    "watchablemedia_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="media.watchablemedia",
                    ),
                ),
                ("Artist", models.CharField(max_length=75)),
                ("Year", models.IntegerField(default=-1)),
            ],
            bases=("media.watchablemedia",),
        ),
    ]