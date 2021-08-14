# Generated by Django 3.2.4 on 2021-06-26 12:50

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0045_alter_roundstat_avg_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='market',
            name='beta',
            field=models.DecimalField(decimal_places=2, help_text="How much should the demand for a trader's product decrease, when (s)he raises the unit price by one?", max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.0000'))]),
        ),
        migrations.AlterField(
            model_name='market',
            name='theta',
            field=models.DecimalField(decimal_places=2, help_text="How much should the demand for a trader's product increase, when the market's average price goes up by one?", max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.0000'))]),
        ),
    ]
