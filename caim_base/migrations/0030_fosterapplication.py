# Generated by Django 4.1 on 2023-06-19 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("caim_base", "0029_fostererprofile_is_complete_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FosterApplication",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACCEPTED", "Accepted"),
                            ("REJECTED", "Rejected"),
                            ("PENDING", "Pending"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "reject_reason",
                    models.TextField(blank=True, max_length=65516, null=True),
                ),
                ("submitted_on", models.DateField(auto_now_add=True)),
                ("updated_on", models.DateField(auto_now=True)),
                (
                    "animal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="caim_base.animal",
                    ),
                ),
                (
                    "fosterer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="caim_base.fostererprofile",
                    ),
                ),
            ],
        ),
    ]
