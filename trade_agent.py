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
from monitoring import MonitoringClient

def urlopen(url, timeout=60, max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': "trade_agent"})
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.URLError as e:
            print(f"Error occurred while making API request: {str(e)}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def coingecko_details(ids):
    all_coins = []
    cmc = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=" + ids
    return json.loads(urlopen(cmc, timeout=5).read().decode('utf-8'))

def flatten(xss):
    return [x for xs in xss for x in xs]

def market_sell(db_wall, wall, amount, ask):
    # Automation can happen here
    notification("Trade Walls: sell %s estimated %.2e %s for %.2e %s" % (wall.pair, amount, lhs, ask, rhs))
    OrderExecution.create(wall=db_wall, amount=amount, total_price=ask, type='sell')

def market_buy(db_wall, wall, amount, bid):
    # Automation can happen here
    notification("Trade Walls: buy %s estimated %.2e %s for %.2e %s" % (wall.pair, amount, lhs, bid, rhs))
    OrderExecution.create(wall=db_wall, amount=amount, total_price=bid, type='buy')

def get_market_trade_history(db_wall):
    return [(order.type, (Decimal(order.total_price), Decimal(order.amount))) for order in db_wall.executions]

def process_walls():
    # Query all Wall objects
    db_walls = Wall.select()
    if db_walls.count() == 0:
        # Use the id from coingecko url, such as ethereum from https://www.coingecko.com/en/coins/ethereum
        print("Creating fake walls")
        Wall.create(bid_price="6", ask_price="12", pair="near/nano", keep="10", quantity="10")
        db_walls = Wall.select()

    walls = []
    # Print each Wall object
    for wall in db_walls:
        unit = wall.pair.split("/")[1]
        token = wall.pair.split("/")[0]
        print(f"{wall.pair} Bid Price: {wall.bid_price} {unit}, Ask price: {wall.ask_price} {unit}, Keep: {wall.keep} {token}, Quantity: {wall.quantity}")
        walls.append(Walls(pair=wall.pair, bid_price=Decimal(wall.bid_price), ask_price=Decimal(wall.ask_price), keep=Decimal(wall.keep), quantities=[Decimal(wall.quantity)]))

    total_potential = {}
    for db_wall, wall in zip(db_walls, walls):
        history = get_market_trade_history(db_wall)
        base = wall.pair.split("/")[1]
        if base not in total_potential:
            total_potential[base] = 0
        print("Potential spend for", ("%-12s" % wall.pair.split("/")[0]), ("%-5.2f %s" % (wall.potential_spend(history=history)[1], wall.pair.split("/")[1])))
        total_potential[base] += wall.potential_spend(history=history)[1]

    for coin in total_potential.keys():
        print("Total potential spend for ", coin, "=", ("%.2f" % total_potential[coin]))

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
    for db_wall, wall in zip(db_walls, walls):
        pair = wall.pair
        lhs = pair.split("/")[0]
        rhs = pair.split("/")[1]
        lhs_usd_price, rhs_usd_price = prices[lhs], prices[rhs]
        unit_price = Decimal(lhs_usd_price) / Decimal(rhs_usd_price)
        history = get_market_trade_history(db_wall)
        print(wall.pair, "Current price", ("%-5.2f %s per %s" % (unit_price, rhs, lhs)))
        proposed_action = wall.step(Decimal(unit_price), history)
        for h in history:
            print(" -", h)
        if proposed_action is not None and proposed_action[0] == "buy":
            market_buy(db_wall, wall, proposed_action[1][1], proposed_action[1][0])
        if proposed_action is not None and proposed_action[0] == "sell":
            market_sell(db_wall, wall, proposed_action[1][1], proposed_action[1][0])

def main():
    while True:
        try:
            process_walls()
            monitoring_client.record_success()
            time.sleep(60)  # Sleep for 60 seconds before the next iteration
        except Exception as e:
            monitoring_client.record_error(str(e))
            print("An error occurred:", str(e))
            time.sleep(60)  # Sleep for 60 seconds before retrying


if __name__ == "__main__":
    main()
