# Generated by Django 3.1 on 2021-04-23 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20210421_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatus',
            name='tag_points',
            field=models.IntegerField(default=0),
        ),
    ]
