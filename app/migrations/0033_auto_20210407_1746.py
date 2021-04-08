# Generated by Django 3.1 on 2021-04-07 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_auto_20210406_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fleet',
            name='command_order',
            field=models.IntegerField(choices=[(0, 'Attack Planet'), (1, 'Station On Planet'), (2, 'Move To System'), (3, 'Merge In System'), (4, 'Merge In System A'), (5, 'Join Main Fleet'), (6, 'Perform Operation'), (7, 'Perform Incantation'), (8, 'Stationed'), (10, 'Explore Planet')], default=0),
        ),
    ]
