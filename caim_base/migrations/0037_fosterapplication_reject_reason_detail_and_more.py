# Generated by Django 4.1 on 2023-08-02 13:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caim_base", "0036_alter_awg_awg_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="fosterapplication",
            name="reject_reason_detail",
            field=models.TextField(blank=True, max_length=65516, null=True),
        ),
        migrations.AlterField(
            model_name="fosterapplication",
            name="reject_reason",
            field=models.CharField(
                choices=[
                    (
                        "UNSUITABLE",
                        "Not suitable for the animal requested, and not willing to consider alternative",
                    ),
                    ("UNRELIABLE", "Concerns about fosterer reliability/commitment"),
                    ("PROPERTY", "Concerns with home and/or yard situation"),
                    ("HUMAN_ROOMMATES", "Concerns with the people in the home"),
                    ("PET_ROOMMATES", "Concerns with the other pets in the home"),
                    ("NO_LANDLORD_APPROVAL", "Landlord has not approved fostering"),
                    ("LIED", "Lied on Application"),
                    ("OTHER", "Other"),
                ],
                default="OTHER",
                max_length=32,
            ),
        ),
    ]
