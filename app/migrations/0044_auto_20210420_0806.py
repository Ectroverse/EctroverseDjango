# Generated by Django 3.1 on 2021-04-20 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_empire_artefacts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empire',
            name='artefacts',
            field=models.ManyToManyField(to='app.Artefacts'),
        ),
    ]
