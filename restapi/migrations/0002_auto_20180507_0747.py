# Generated by Django 2.0.2 on 2018-05-07 07:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supervisor',
            name='user',
        ),
        migrations.AlterField(
            model_name='specificdate',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='birthday',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
