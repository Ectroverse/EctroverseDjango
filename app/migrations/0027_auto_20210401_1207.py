# Generated by Django 3.1 on 2021-04-01 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20210329_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='news_type',
            field=models.CharField(choices=[('SA', 'Successfull Attack'), ('UA', 'Unsuccessfull Attack'), ('SD', 'Successfull Defence'), ('UD', 'Unsuccessfull Defence'), ('SE', 'Successfull Exploration'), ('UE', 'Unsuccessfull Exploration'), ('PA', 'Psychic Attack'), ('PD', 'Psychic Defence'), ('AA', 'Agent Attack'), ('AD', 'Agent Defence'), ('GA', 'Ghost Attack'), ('GD', 'Ghost Defence'), ('SI', 'Sent aid'), ('RA', 'Requested aid'), ('M', 'Market operation'), ('N', 'None'), ('BB', 'Buildings Built'), ('UB', 'Units Built'), ('MS', 'Message Sent'), ('MR', 'Message Reseived'), ('RWD', 'Relation War Declared'), ('RWE', 'Relation War Ended'), ('RNP', 'Relation Nap Proposed'), ('RND', 'Relation Nap Declared'), ('RNE', 'Relation Nap Ended'), ('RAP', 'Relation Alliance Proposed'), ('RAD', 'Relation Alliance Declared'), ('RAE', 'Relation Alliance Ended'), ('FS', 'Fleet Stationed'), ('FU', 'Fleet Station Unsuccessful'), ('FM', 'Fleet Merged'), ('FJ', 'Fleet Joined Main'), ('E', 'Something Extra')], default='N', max_length=3),
        ),
    ]
