# Generated by Django 3.1 on 2021-03-29 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_mapsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapsettings',
            name='faction',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faction', to='app.userstatus'),
        ),
    ]
