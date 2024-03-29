# Generated by Django 4.1 on 2023-08-02 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caim_base", "0039_alter_fostererexistingpetdetail_type_of_animals"),
    ]

    operations = [
        migrations.AddField(
            model_name="fostererprofile",
            name="num_people_in_home",
            field=models.IntegerField(
                blank=True,
                default=None,
                null=True,
                verbose_name="How many people live in your home, including yourself?",
            ),
        ),
        migrations.AddField(
            model_name="fostererprofile",
            name="people_in_home_detail",
            field=models.TextField(
                blank=True,
                default=None,
                null=True,
                verbose_name="Please list the following details for each person in your home, excluding yourself: Name, Relation, Age, Email address.",
            ),
        ),
    ]
