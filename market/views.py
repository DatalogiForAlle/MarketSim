from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse

from random import randint

from .models import Market, Trader, Trade
from decimal import Decimal
from .forms import MarketForm, TraderForm, TradeForm

@require_GET
def home(request):
    return render(request, 'market/home.html')

def create(request):
    if request.method == 'POST':
        form = MarketForm(request.POST)
        if form.is_valid():
            new_market = form.save()
            return HttpResponseRedirect(reverse('market:monitor', args=(new_market.market_id,)))
    elif request.method == 'GET':
        form = MarketForm()
    return render(request, 'market/create.html', {'form': form})

def join(request):
    if request.method == 'POST':
        form = TraderForm(request.POST)
        if form.is_valid():
            market = Market.objects.get(market_id=form.cleaned_data['market_id'])
            new_trader = Trader.objects.create(
                market = market,
                name = form.cleaned_data['username'],
                prod_cost = randint(market.min_cost, market.max_cost),
                balance = Trader.initial_balance
            )
            request.session['trader_id'] = new_trader.pk
            return HttpResponseRedirect(reverse('market:play', args=(market.market_id,)))
    elif request.method == 'GET':
        if 'market_id' in request.GET:
            form = TraderForm(
                initial={'market_id': request.GET['market_id']})
        else:
            form = TraderForm()
    return render(request, 'market/join.html', {'form':form})



def monitor(request, market_id):

    market = get_object_or_404(Market, market_id=market_id)
    traders = Trader.objects.filter(market=market)
    context = {
        'market': market,    
        'traders': traders,
        'rounds': range(market.round),
        'max_num_players': range(30)

    }
    if request.method == "GET":
        return render(request, 'market/monitor.html', context)

    if request.method == "POST":
        #ikke ordentligt testet
        for trader in traders:
            traders_num_trades = Trade.objects.filter(trader=trader, round=market.round).count()
            assert(traders_num_trades == 0 or traders_num_trades ==1)
            # if trader has not traded this round, make a forced trade: 
            if traders_num_trades == 0:
                Trade.objects.create(
                    trader=trader, 
                    unit_price=0,
                    unit_amount=0,
                    was_forced=True
                )
        trades = Trade.objects.filter(round=market.round).filter(market=market)
        assert(len(trades) > 0), "No trades in market this round. Can't calculate avg. price."
        assert(len(trades) == len(traders)), "Num trades does equal num traders."
        alpha, beta, theta = market.alpha, market.beta, market.theta
        avg_price = sum([trade.unit_price for trade in trades]) / len(trades)
        profit = []
        for trade in trades:
            demand = alpha - beta * Decimal(trade.unit_price) + theta*Decimal(avg_price)
            expenses = trade.trader.prod_cost * trade.unit_amount
            income = trade.unit_price * min(demand, trade.unit_amount)
            trade_profit = income - expenses
            trade.profit = trade_profit
            trader = trade.trader
            balance_before_trade = trader.balance
            trader.balance += trade_profit 
            trade.balance_after = balance_before_trade + trade_profit
            trader.save()
            trade.save()
        market.round += 1
        market.save()

        return HttpResponseRedirect(reverse('market:monitor', args=(market.market_id,)))
    

def validate_market_and_trader(session, market_id):
    """ 
    helper function that checks the following:
    1) There is a market with the given id
    2) There is a trader_id in the current session
    3) This trader exists in database
    3) The trader is on the market given by the market_id, and not some other market
    """
    try:
        market = Market.objects.get(pk=market_id)
    except:
        return {'error_redirect':HttpResponseRedirect(reverse('market:join'))}

    if 'trader_id' not in session:
        return {'error_redirect': HttpResponseRedirect(reverse('market:join') + f'?market_id={market_id}')}
    else:
        pk = session['trader_id']
        try:
            trader = Trader.objects.get(pk=session['trader_id'])
        except:
            return {'error_redirect': HttpResponseRedirect(reverse('market:join') + f'?market_id={market_id}')}
        else:
            if trader.market.market_id != market_id:
                return {'error_redirect': HttpResponseRedirect(reverse('market:join'))}
            else: 
                return {'market': market, 'trader': trader}

        
def play(request, market_id):

    validation = validate_market_and_trader(request.session, market_id)
    
    if 'error_redirect' in validation:
        return validation['error_redirect']
 
    market = validation['market']
    trader = validation['trader']

    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            new_trade = form.save(commit=False)
            new_trade.trader = trader
            new_trade.save()
            return HttpResponseRedirect(reverse('market:wait', args=(market.market_id,)))

        return render(request, 'market/play.html', {'form': form})

    elif request.method == 'GET':
        form = TradeForm()
    
    return render(request, 'market/play.html', {'market':market, 'trader':trader, 'form':form})

@require_GET
def wait(request, market_id):
    validation = validate_market_and_trader(request.session, market_id)
    if 'error_redirect' in validation:
        return validation['error_redirect']   
    context = validation 
    return render(request, 'market/wait.html', context)

@require_GET
def traders_this_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    round = market.round
    traders = [trade.trader.name for trade in Trade.objects.filter(market=market).filter(round=round)]
    data = {
        'traders':traders
    }
    return JsonResponse(data)


@require_GET
def trader_api(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    traders = [
        {
            'name': trader.name,
            'prod_cost': trader.prod_cost,
            'balance': trader.balance,
            'ready': trader.is_ready()
        }
        for trader in Trader.objects.filter(market=market)
    ]
    num_ready_traders = Trade.objects.filter(market=market).filter(round=market.round).count()

    data = {
        'traders': traders,
        'num_traders':len(traders),
        'num_ready_traders': num_ready_traders,

    }
    return JsonResponse(data)


@require_GET
def current_round(request, market_id):
    market = get_object_or_404(Market, market_id=market_id)
    data = {
        'round':market.round
    }
    return JsonResponse(data)

"""
def download(request, market_id):
    # not properly tested yet
    # known issues: 
    # if trader_stats does not exist for all traders in all rounds script will crash. 
    market = get_object_or_404(Market, market_id=market_id)
    market_traders = Trader.objects.filter(market=market)
    total_rounds = market.round
    data = "Round,Average price,Average amount,Average profit,"
    for trader in market_traders:
        data += trader.name + " balance,"
    data += "<br>"
    for r in range(total_rounds):
        data += str(r) + ","
        round_stats = Stats.objects.filter(round=r, market=market)
        avg_price = sum([trader.price for trader in round_stats]) / len(round_stats)
        data += str(avg_price) + ","
        avg_amount = sum([trader.amount for trader in round_stats]) / len(round_stats)
        data += str(avg_amount) + ","
        avg_profit = sum([trader.profit for trader in round_stats]) / len(round_stats)
        data += str(avg_profit) + ","
        for trader in market_traders:
            trader_stats = Stats.objects.get(round=r, market=market, trader=trader)
            data += str(trader_stats.balance) + ","
        data += "<br>"
    output = open(market.market_id + "_stats.csv", "w")
    output.write(data)
    output.close()
    return HttpResponse(data)
"""
