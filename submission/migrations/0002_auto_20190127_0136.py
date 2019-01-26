# Generated by Django 2.1.4 on 2019-01-26 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_contest_is_active'),
        ('problem', '0001_initial'),
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='contest_id',
        ),
        migrations.AddField(
            model_name='submission',
            name='contest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Contest'),
        ),
        migrations.AddField(
            model_name='submission',
            name='language',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='submission',
            name='problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='problem.Problem'),
        ),
        migrations.AddField(
            model_name='submission',
            name='source',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='status',
            field=models.SmallIntegerField(default=0),
        ),
    ]
