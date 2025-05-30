# Generated by Django 5.1.7 on 2025-04-25 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("versions", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="version",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="version",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="version",
            name="name",
            field=models.CharField(max_length=255),
        ),
    ]
