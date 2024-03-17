import math
from decimal import Decimal, Context

class Walls:
    def __init__(self, pair=None, bid_price=0, ask_price=None, quantities=[], keep=0, spread=2, selloff=0, sell_first=False):
        """
        Initializes a new instance of the Walls class with specified trading parameters.

        Parameters:
        - pair (str, optional): The trading pair (e.g., "NEAR/NANO" or "NANO/NANO").
        - bid_price (float): The minimum price level for the trading strategy. Example: 0.4 for NEAR, meaning the lowest buy price.
        - ask_price (float): The maximum price level for the trading strategy. Example: 0.6 for NEAR, meaning the highest sell price.
        - quantities (list): A list of amounts (integers or floats) representing the size of each wall. Example: [10, 20, 40] indicating three quantities.
        - keep (float): The minimum amount of the asset to hold. Example: 10 NEAR.
        - spread (int): The multiplier used to calculate the price difference between quantities. Example: 2, meaning each wall is twice the price of the previous.
        - selloff (float): The fraction of holdings to sell off when a sell condition is met. Example: 0.5, sell half of the holdings.
        - sell_first (bool): Indicates whether to sell before buying when initiating the strategy. Example: False, meaning buy actions are prioritized.

        Example Usage:
        wall = Walls(pair="NEAR/NANO", bid_price=0.4, ask_price=0.6, quantities=[10, 20, 40], keep=10, spread=2)
        """
        assert(ask_price >= bid_price, "ask_price must be > than bid_price for " + pair)
        self.sell_first = sell_first
        self.pair = pair
        self.bid_price = bid_price
        self.ask_price = ask_price
        self.spread = spread
        self.ctx = Context(prec=8)
        self.keep = keep
        self.buy_amounts = []
        self.buy_prices = []
        self.sell_prices = []
        self.selloff = self.ctx.create_decimal_from_float(selloff)
        level = 0
        self.buy_quantities = quantities
        self.sell_quantities = quantities
        for quantity in quantities:
            unit_price = self.bid_price / (spread** level)
            level +=1
            self.buy_prices.append(unit_price)
            self.buy_amounts.append(quantity)
        self.sell_amounts = []
        level = 0
        for quantity in self.sell_quantities:
            unit_price = self.ask_price * (spread** level)
            level +=1
            self.sell_prices.append(unit_price)
            self.sell_amounts.append(quantity)
        total_cost = 0.0
        total_profit = 0.0

    def potential_spend(self, history=None):
        """
        Calculates the potential spending based on the current trading strategy and optionally, a history of past actions.

        Parameters:
        - history (list of tuples, optional): A history of past trading actions, where each action is represented as a tuple ('buy' or 'sell', (amount, price)).

        Returns:
        - A tuple containing the total number of coins purchased and the total potential spend in decimal format.

        Example:
        Assuming no prior history and a strategy with quantities [10, 20, 40], the potential spend to establish the first wall at a price of 0.4 NEAR/NANO would be 4 NANO.
        """
        result = Decimal(0)
        coins_purchased = Decimal(0)
        if self.sell_first:
            coins_purchased = Decimal(self.buy_quantities[0])
        if history is not None:
            for h in history:
                coins_purchased += h[1][0]

        for amount, price in zip(self.buy_amounts, self.buy_prices):
            amount = Decimal(amount)
            tmp = amount
            amount -= coins_purchased
            coins_purchased -= tmp
            if amount > 0:
                result += Decimal(amount) * Decimal(price)
            if coins_purchased < 0:
                coins_purchased = 0

        mh = self.keep
        mh -= coins_purchased
        coins_purchased -= self.keep
        if mh > 0:
            result += Decimal(mh) * Decimal(self.buy_prices[0])
        return [coins_purchased, result]

    def calculate_holdings(self, history):
        """
        Calculates the current holdings based on a history of trading actions.

        Parameters:
        - history (list of tuples): A history of past trading actions, similar to potential_spend.

        Returns:
        - The current holdings in decimal format.

        Example:
        After executing buy actions from the provided example, the holdings might be 70 NEAR if all walls have been bought into.
        """
        holdings = self.ctx.create_decimal_from_float(0)
        if self.sell_first:
            holdings += Decimal(self.buy_quantities[0])
        for action in history:
            item = action[1]
            if action[0] == 'sell':
                holdings -= item[0]
            if action[0] == 'buy':
                holdings += item[0]

        return holdings

    def profits(self, history):
        """
        Calculates the total profit from trading based on a history of actions.

        Parameters:
        - history (list of tuples): A history of past trading actions, similar to potential_spend.

        Returns:
        - The total profit in decimal format.

        Example Output:
        If after several sell actions at increasing prices, the total profit might be 120 NANO, indicating a successful series of trades.
        """
        sold = self.ctx.create_decimal_from_float(0.0)
        for action in history:
            item = action[1]
            if action[0] == 'sell':
                sold += item[0] * item[1]
            if action[0] == 'buy':
                sold += item[0] * item[1]

        return sold

    def step(self, current_price, history):
        """
        Determines the next trading action based on the current price and a history of past actions.

        Parameters:
        - current_price (float): The current price of the trading pair.
        - history (list of tuples): A history of past trading actions, similar to potential_spend.

        Returns:
        - A tuple representing the proposed action ('buy' or 'sell', (amount, price)), or None if no action is proposed.

        Example:
        At a current price of 0.45 NEAR/NANO, the step method might return ('buy', (10, 0.45)) to buy 10 NEAR at 0.45 NANO each.
        """
        current_price = Decimal(current_price)
        proposed_action = None
        current_holdings = self.calculate_holdings(history)
        available_coins = current_holdings - self.keep
        buy_amount = 0
        sell_amount = 0

        target_amount = self.keep
        active_buy_wall = False
        for price, amount in zip(self.buy_prices, self.buy_amounts):
            if(current_price < price):
                target_amount += amount
                active_buy_wall = True
        buy_amount = target_amount-current_holdings

        if active_buy_wall and buy_amount > 0:
            return ('buy', (buy_amount, current_price))

        amount_needed = self.keep
        active_sell_wall = False
        bid_price_triggered_sell_wall = None
        for price, amount in zip(self.sell_prices, self.sell_amounts):
            if(current_price < price):
                amount_needed += amount
            else:
                active_sell_wall = True
                if bid_price_triggered_sell_wall is None or bid_price_triggered_sell_wall[1] > price:
                    bid_price_triggered_sell_wall = (amount, price)
        sell_amount = current_holdings - amount_needed

        if active_sell_wall:

            if len(history) > 0 and history[-1][0] == 'buy' and self.selloff > 0:
                sell_amount = bid_price(history[-1][1][0] * self.selloff, bid_price_triggered_sell_wall[0])

            if sell_amount > 0:
                return ('sell', (sell_amount, current_price))

        return None

    def print(self):
        """
        Prints a summary of the current trading strategy, including buy and sell walls, unit prices, and other relevant information.

        Example Output:
        --- 
        NEAR/NANO buy wall
        Buy [10, 20, 40] Sell [10, 20, 40]
        Unit price [0.4, 0.8, 1.6] Sell [0.6, 1.2, 2.4]
        ---
        This output indicates the strategy involves buying NEAR at increasing prices and selling at even higher prices.
        """
        print(" --- ")
        print(self.pair, "buy wall")
        print("Buy", self.buy_amounts, "Sell", self.sell_amounts)
        print("Unit price", self.buy_prices, "Sell", self.sell_prices)
        print(" --- ")

if __name__ == '__main__':
    wall = Walls(pair="TEST/NANO", bid_price = 0.4, ask_price = 0.6, quantities=[10,20,40], keep=10, spread=2)
    wall.print()
    i = 0
    actions = []

    for i in range(1502):
        unit_price = (math.sin(0.017*i)+1)/2.0 * 3.0
        #unit_price = (math.sin(0.017*i)+1)/2.0 * 0.4 + 0.3
        proposed_action = wall.step(unit_price, actions)
        if proposed_action is not None:
            actions += [proposed_action]
        if i % 100 == 1:
            print(i, "Total profit TEST", wall.calculate_holdings(actions))
            print(i, "Total profit NANO", wall.profits(actions))

    assert(wall.calculate_holdings(actions) > 0)
    assert(wall.profits(actions) > 0)
    # melt down
    for i in range(1000):
        unit_price = 0.99*unit_price
        proposed_action = wall.step(unit_price, actions)
        if proposed_action is not None:
            actions += [proposed_action]
    assert(wall.calculate_holdings(actions) == 80)
    # melt up
    for i in range(1000):
        unit_price = 1.02*unit_price
        proposed_action = wall.step(unit_price, actions)
        if proposed_action is not None:
            actions += [proposed_action]
    assert(wall.profits(actions) > 0)
    assert(wall.calculate_holdings(actions) > 0)


    for action in actions:
        print(action)

    print("Total profit TEST", wall.calculate_holdings(actions))
    print("Total profit NANO", wall.profits(actions))
