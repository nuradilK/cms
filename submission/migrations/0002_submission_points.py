# Generated by Django 2.1.4 on 2019-03-22 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
