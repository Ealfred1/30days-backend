# Generated by Django 5.1.7 on 2025-04-29 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("versions", "0002_alter_version_options_alter_version_description_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="version",
            options={"ordering": ["-number"]},
        ),
        migrations.AddField(
            model_name="version",
            name="codename",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="version",
            name="focus_area",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="version",
            name="technologies",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name="version",
            name="number",
            field=models.IntegerField(unique=True),
        ),
    ]
