# Generated by Django 3.1 on 2021-04-18 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_auto_20210418_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatus',
            name='energy_specop_effect',
            field=models.BigIntegerField(default=0),
        ),
    ]
