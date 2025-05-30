# Generated by Django 5.1.7 on 2025-04-21 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Activity",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("submission", "Submitted Project"),
                            ("review", "Reviewed Project"),
                            ("rating", "Rated Project"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "activities",
                "ordering": ["-created_at"],
            },
        ),
    ]
