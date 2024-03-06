import requests
import urllib
import time
import datetime
from decimal import Decimal, getcontext, localcontext
import os
import json
from walls import Walls
from notification import notification
from db import Wall, OrderExecution

def urlopen(url, timeout=60):
    req = urllib.request.Request(url, headers={'User-Agent' : "trade_agent"})
    return urllib.request.urlopen(req, timeout=timeout)

def coingecko_details(ids):
    all_coins = []
    cmc = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids="+ids
    return json.loads(urlopen(cmc, timeout=5).read().decode('utf-8'))

def flatten(xss):
    return [x for xs in xss for x in xs]

def market_sell(token, pair, amount, ask):
    # Automation can happen here
    notification("Trade Walls: sell %s estimated %.2e %s for %.2e %s" % (wall.pair, amount, lhs, cost, rhs ))

def market_buy(token, pair, amount, bid, wallet_balance, precision=8):
    # Automation can happen here
    notification("Trade Walls: buy %s estimated %.2e %s for %.2e %s" % (wall.pair, amount, lhs, cost, rhs ))

def get_market_trade_history(pair):
    return []

# Query all Wall objects
db_walls = Wall.select()
if db_walls.count() == 0:
    # Use the id from coingecko url, such as ethereum from https://www.coingecko.com/en/coins/ethereum
    print("Creating fake walls")
    Wall.create(bid_price="1", ask_price="4", pair="near/nano", keep="10", quantity="10")
    db_walls = Wall.select()

# Print each Wall object
for wall in db_walls:
    unit = wall.pair.split("/")[1]
    token = wall.pair.split("/")[0]
    print(f"{wall.pair} Bid Price: {wall.bid_price} {unit}, Ask price: {wall.ask_price} {unit}, Keep: {wall.keep} {token}, Quantity: {wall.quantity}")


total_potential = {}
for wall in walls:
    base = wall.pair.split("/")[1]
    if base not in total_potential:
        total_potential[base] = 0
    print("Potential spend for",("%-12s" % wall.pair.split("/")[0]), ("%-5.2f %s" % (wall.potential_spend()[1], wall.pair.split("/")[1])))
    total_potential[base] += wall.potential_spend()[1]

for coin in total_potential.keys():
    print("Total potential spend in :", coin, ":", ("%.2f" % total_potential[coin]))

coins = [wall.pair.split("/") for wall in walls]
coins = list(set(flatten(coins)))
details = coingecko_details(",".join(coins))
prices = {}
for coin in coins:
    found = False
    for d in details:
        if d['id'] == coin:
            prices[coin] = d['current_price']
            found = True
            break
    if not found:
        print("Can't find price for", coin)

ask_cache = {}
bid_cache = {}
for wall in walls:
    pair = wall.pair
    lhs = pair.split("/")[0]
    rhs = pair.split("/")[1]
    lhs_usd_price, rhs_usd_price = prices[lhs], prices[rhs]
    unit_price = Decimal(lhs_usd_price)/Decimal(rhs_usd_price)
    history = get_market_trade_history(wall.pair)
    actions = []
    for trade in history:
        amount = Decimal(trade.amount)
        price = Decimal(trade.price)
        actions.append((trade.action, (amount, price)))

    print(wall.pair, "Current price", ("%-5.2f %s per %s" % (unit_price, rhs, lhs)))
    proposed_action = wall.step(Decimal(unit_price), actions)
    #print("BUY", proposed_action, "SELL", proposed_action)
    #wall.print()
    #for h in history:
    #    print(" -",h)
    #print(proposed_action, proposed_action)
    #print("HAVE", wall.calculate_holdings(actions), proposed_action)
    if proposed_action is not None and proposed_action[0] == "buy":
        market_buy(token, wall.pair, proposed_action[1][0], proposed_action[1][1], wallet_balance)
    if proposed_action is not None and proposed_action[0] == "sell":
        market_sell(token, wall.pair, proposed_action[1][0], proposed_action[1][1])
