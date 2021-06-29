import factory

from django.test import TestCase
from ..models import Market, Trader, Trade, RoundStat
from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    
    username = factory.Sequence(lambda n: 'john%s' % n)
    email = 'JohnDoe@example.com'
    password = factory.PostGenerationMethodCall('set_password',
                                                'defaultpassword')


class MarketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Market 

    product_name_singular = 'baguette'
    product_name_plural = 'baguettes'
    initial_balance = Decimal('5000.00')
    alpha = Decimal('105.0000')
    beta = Decimal('17.5000')
    theta = Decimal('14.5800')
    min_cost = Decimal('8.00')
    max_cost = Decimal('8.00')
    created_by = factory.SubFactory(UserFactory)



class TraderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trader
    market = factory.SubFactory(MarketFactory)
    name = factory.Sequence(lambda n: 'eva%s' % n)
    balance = Decimal('4734.23')
    prod_cost = Decimal('8.00')

def round_to_int(number):
    """ Re-naming is needed since 'round' is also the name of a field in TradeFactory """
    return round(number)

class TradeFactory(factory.django.DjangoModelFactory):
    """ Mimics a regular trade that has been processed (after host has finished round) """
    class Meta:
        model = Trade
    
    trader = factory.SubFactory(TraderFactory)
    unit_price = Decimal('10.20')
    unit_amount = 13
    demand = max(0, round_to_int(MarketFactory.alpha - MarketFactory.beta*unit_price  + MarketFactory.theta * Decimal('12.32'))) # 12.32 is stand in for market avg. prce 
    units_sold = min(demand, unit_amount) 
    profit = Decimal(units_sold * unit_price - unit_amount * TraderFactory.prod_cost)
    balance_after = Decimal(TraderFactory.balance)
    round = 37

class UnProcessedTradeFactory(factory.django.DjangoModelFactory):
    """ Mimics a regular trade that has not been processed (before host has finished round) """     
    class Meta:
        model = Trade

    trader = factory.SubFactory(TraderFactory)
    unit_price = Decimal('10.20')
    unit_amount = 13
    round = 37

class ForcedTradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trade

    trader = factory.SubFactory(TraderFactory)
    was_forced = True
    balance_after = Decimal(TraderFactory.balance)
    round = 37
