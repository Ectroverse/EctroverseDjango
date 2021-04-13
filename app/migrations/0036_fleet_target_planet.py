# Generated by Django 3.1 on 2021-04-13 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20210413_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='fleet',
            name='target_planet',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='target', to='app.planet'),
        ),
    ]
