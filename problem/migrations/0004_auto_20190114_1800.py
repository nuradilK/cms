# Generated by Django 2.1.4 on 2019-01-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0003_problem_testset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='testset',
            field=models.CharField(default='tests', max_length=100),
        ),
    ]
