# Generated by Django 4.1 on 2023-06-26 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("caim_base", "0031_awgmember_canmanageapplications"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animal",
            name="awg",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="animals",
                to="caim_base.awg",
                verbose_name="AWG",
            ),
        ),
        migrations.AlterField(
            model_name="fosterapplication",
            name="animal",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="caim_base.animal"
            ),
        ),
        migrations.AlterField(
            model_name="fosterapplication",
            name="fosterer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="caim_base.fostererprofile"
            ),
        ),
    ]
