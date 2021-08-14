from django.test import TestCase
from ..models import Market, Trader, Trade, RoundStat
from django.contrib.auth import get_user_model
from decimal import Decimal 
from .factories import MarketFactory, TradeFactory, UserFactory, TraderFactory

class MarketModelTest(TestCase):
    """ All relevant properties are currently being tested in the test_factories test suite """
    pass
    

class TraderModelTest(TestCase):
    """ All relevant properties are currently being tested in the test_factories test suite """
    pass

class TradeModelTest(TestCase):
    """ Most properties are being tested in the test_factories test suite """
       
    def test_constraint_trader_and_round_unique_together(self):
        """ There can only be one trade pr trader pr round """
        trade = TradeFactory(round=17)    
        # we try to make a trade with same trader and same round - this should cast an integrity error in the database
    
        try:
            Trade.objects.create(
                trader=trade.trader, round=17)
            error_mgs = "there was no error"
        except:
            error_mgs = "error message"
        finally:
            self.assertEqual(error_mgs, "error message")
    
    def test_constraint_trade_and_round_unique_together_okay_to_update_trade(self):
        """ updating a trade will not cast an integrity error """
        trade = TradeFactory(round=17)
        try:
            trade.balance_after = 400
            trade.save()
            mgs = "there was no error"
        except:
            mgs = "error message"
        finally:
            self.assertEqual(mgs, "there was no error")
        trade.refresh_from_db()
        self.assertEqual(trade.balance_after, 400)

class TestRoundStatModel(TestCase):

    def test_object_creation_and_name(self):
        market = MarketFactory()
        r1 = RoundStat.objects.create(market=market, round=3, avg_price=Decimal('34.34')) 
        self.assertIsInstance(r1, RoundStat)
        self.assertEqual(r1.market, market)
        self.assertEqual(r1.round, 3)
        self.assertEqual(r1.avg_price, Decimal('34.34'))
        self.assertEqual(str(r1), f"{market.market_id}[3]")


    def test_market_and_round_uinque_together(self):
        """ There can only be one roundstat object pr market pr round """
        market1 = MarketFactory()
        market2 = MarketFactory()

        RoundStat.objects.create(
            market=market1, round=3, avg_price=34.343)

        # it should be possible to create another object with same market, but different round
        s1 = RoundStat.objects.create(market=market1, round=45, avg_price=34.343)
        self.assertIsInstance(s1, RoundStat)

        # it should be possible to create another object with same same round, but different market
        s2 = RoundStat.objects.create(
            market=market2, round=3, avg_price=34.343)
        self.assertIsInstance(s2, RoundStat)

        # it should not be possible to possible to create another object with same round and market
        try: 
            RoundStat.objects.create(
                market=market1, round=3, avg_price=100)
            mgs="No error happend"
        except:
            mgs = "An error happened"
        finally:
            self.assertEqual(mgs, "An error happened")



           
