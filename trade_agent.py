import requests
import time
import datetime
from decimal import Decimal, getcontext, localcontext
import os
import json
from walls import Walls

def market_sell(token, pair, amount, ask, precision=8):
    print("MARKET SELL", token, pair, amount, ask, precision)

def market_buy(token, pair, amount, bid, wallet_balance, precision=8):
    print("MARKET BUY", token, pair, amount, bid, wallet_balance, precision)

def bid_price(token, base):
    # time.sleep(1)
    return 0.1

def ask_price(token, base):
    # time.sleep(1)
    return 0.2

def token_list():
    return [{"symbol": "NANO", "precision": 30}, {"symbol": "NEAR", "precision": 8}]

def get_wallet_balance():
    return Decimal(1.0)

def get_market_trade_history(pair):
    return []

walls = [
  Walls(pair="NEAR/NANO", min = Decimal("0.4"), max = Decimal("2.0"), walls=[10])
]

total_potential = 0
for wall in walls:
    print("Potential spend for",("%-12s" % wall.pair.split("/")[0]), ("%-5.2f %s" % (wall.potential_spend()[1], wall.pair.split("/")[1])))
    total_potential += wall.potential_spend()[1]

print("Total potential spend:", ("%.2f" % total_potential))

precision_map = {}
for token in token_list():
    precision_map[token["symbol"]] = int(token["precision"])

#with open("owner-lp.key", "r") as key_file:
#    owner_key = key_file.read().rstrip()
#    # TODO load account

wallet_balance = Decimal(get_wallet_balance())

ask_cache = {}
bid_cache = {}
for wall in walls:
    if ":" in wall.pair:
        pair = wall.pair.split(":")[1]
    else:
        pair = wall.pair
    token = pair.split("/")[0]
    base = pair.split("/")[1]
    if ":" in token:
        token = token.split(":")[1]
    if token not in ask_cache:
        ask_cache[token] = ask_price(token, base)
    unit_price_ask = ask_cache[token]
    if token not in bid_cache:
        bid_cache[token] = bid_price(token, base)
    unit_price_bid = bid_cache[token]
    history = get_market_trade_history(wall.pair)
    actions = []
    for trade in history:
        amount = Decimal(trade.amount)
        price = Decimal(trade.price)
        buy_or_sell = trade.action
        actions.append((buy_or_sell, (amount, price)))
    if(unit_price_ask is None or unit_price_bid is None):
        continue
    print(wall.pair, "Current bid", unit_price_bid, "Current ask", unit_price_ask)
    proposed_buy_action = wall.step(Decimal(unit_price_ask), actions)
    proposed_sell_action = wall.step(Decimal(unit_price_bid), actions)
    #print("BUY", proposed_buy_action, "SELL", proposed_sell_action)
    #wall.print()
    #for h in history:
    #    print(" -",h)
    holdings = wall.calculate_holdings(actions)
    print(holdings, token, "owned")
    #print(proposed_buy_action, proposed_sell_action)
    #print("HAVE", wall.calculate_holdings(actions), proposed_sell_action)
    if proposed_buy_action is not None:
        if proposed_buy_action[0] == "buy":
            print(wall.pair, proposed_buy_action, "with", wallet_balance, base)
            bought = market_buy(token, wall.pair, proposed_buy_action[1][0], proposed_buy_action[1][1], wallet_balance, precision=precision_map[token])
            if bought is None:
                continue
            wallet_balance -= bought
    if proposed_sell_action is not None:
        if proposed_sell_action[0] == "sell":
            print(wall.pair, proposed_sell_action)
            sold = market_sell(token, wall.pair, proposed_sell_action[1][0], proposed_sell_action[1][1], precision=precision_map[token])
            if sold is None:
                continue
            print("Sold", sold, base, 'worth of', token)
