# Generated by Django 4.1 on 2023-08-04 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("caim_base", "0043_alter_fosterapplication_reject_reason"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fostererpersoninhomedetail",
            name="age",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="fostererpersoninhomedetail",
            name="name",
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
    ]
