# Generated by Django 3.2.4 on 2021-08-23 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0059_alter_market_max_rounds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='max_rounds',
            field=models.IntegerField(default=15),
        ),
    ]
