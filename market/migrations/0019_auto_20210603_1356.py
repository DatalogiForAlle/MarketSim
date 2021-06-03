# Generated by Django 3.1.11 on 2021-06-03 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0018_auto_20210601_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='max_cost',
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='market',
            name='min_cost',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='market',
            name='round',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
