# Generated by Django 4.1 on 2022-09-15 10:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("caim_base", "0007_awgmember"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="awgmember",
            unique_together={("user", "awg")},
        ),
    ]
