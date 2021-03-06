# Generated by Django 3.1 on 2021-04-13 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20210410_1916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fleet',
            name='target_planet',
        ),
        migrations.AddField(
            model_name='specops',
            name='stealth',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='fleet',
            name='command_order',
            field=models.IntegerField(choices=[(0, 'Attack Planet'), (1, 'Station On Planet'), (2, 'Move To System'), (3, 'Merge In System'), (4, 'Merge In System A'), (5, 'Join Main Fleet'), (6, 'Perform Operation'), (7, 'Perform Incantation'), (10, 'Explore Planet')], default=0),
        ),
        migrations.AlterField(
            model_name='fleet',
            name='on_planet',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.planet'),
        ),
    ]
