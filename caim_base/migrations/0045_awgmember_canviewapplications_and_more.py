# Generated by Django 4.1 on 2023-08-07 15:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caim_base", "0044_alter_fostererpersoninhomedetail_age_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="awgmember",
            name="canViewApplications",
            field=models.BooleanField(default=False),
        ),
    ]
