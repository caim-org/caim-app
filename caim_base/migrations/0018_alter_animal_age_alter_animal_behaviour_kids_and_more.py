# Generated by Django 4.1 on 2022-10-19 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("caim_base", "0017_remove_awg_is_published"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animal",
            name="age",
            field=models.CharField(
                choices=[
                    ("BABY", "Puppy (< 1 year)"),
                    ("YOUNG", "Young (1-3 years)"),
                    ("ADULT", "Adult (3-8 years)"),
                    ("SENIOR", "Senior (8+ years)"),
                ],
                max_length=8,
            ),
        ),
        migrations.AlterField(
            model_name="animal",
            name="behaviour_kids",
            field=models.CharField(
                choices=[
                    ("POOR", "Poor"),
                    ("SELECTIVE", "Selective"),
                    ("GOOD", "Good"),
                    ("NOT_TESTED", "Not tested"),
                ],
                default="NOT_TESTED",
                max_length=10,
                verbose_name="Behavour with kids",
            ),
        ),
        migrations.AlterField(
            model_name="animal",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="animal",
            name="size",
            field=models.CharField(
                choices=[
                    ("S", "Small (0-25 lbs)"),
                    ("M", "Medium (26-60 lbs)"),
                    ("L", "Large (61-100 lbs)"),
                    ("XL", "X-Large (101 lbs+)"),
                ],
                max_length=2,
            ),
        ),
    ]