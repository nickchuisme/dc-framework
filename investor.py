import numpy as np
import matplotlib.pyplot as plt

class Investor:

    def __init__(self, threshold, balance, print_order=False, fee=1):
        # initial setting of class
        self.threshold  = threshold
        self.orders = dict()
        self.step = 0
        self.transaction_fee = fee

        # records of fundamental info
        self.balance = balance
        self.invest = 0
        self.profits = [[0, 0]]
        self.profits_with_fee = [[0, 0]]
        self.order_record = [0, 0]
        self.volume_record = [0, 0]

        self.print_order = print_order

        # buy price
        self.buy_p = None
        # profit price
        self.profit_p = None
        # price of stop loss
        self.stop_p = None

    def buy_order(self, price, vol):
        if vol > 0 and self.balance - (price * vol) >= 0:
            self.orders[self.step] = (price, vol)
            self.balance -= price * vol
            self.invest += price * vol
            self.profits_with_fee.append([0 - self.transaction_fee, self.step - 1])
            if self.print_order:
                print(f'[Buy Order ({self.step - 1})] price: {price}, volume: {vol}')

    def sell_order(self, price):
        if self.orders:
            volumes, profits = 0, 0
            for p, v in self.orders.values():
                profit = round((price - p) * v, 5)
                self.balance += price * v
                profits += profit
                volumes += v
                self.update_records(profit, v)
            self.profits_with_fee.append([profits - self.transaction_fee, self.step - 1])

            # reset buy prices and order list
            self.orders = dict()
            self.buy_p = None
            if self.print_order:
                print(f'[Sell Order ({self.step - 1})] price: {price}, volume: {volumes}, profit: {round(profits, 5)}')

    def action(self, price, price_ie, signal, trade=True):
        self.step += 1

        if trade:
            # obtain strategy with signal
            self.buy_p, self.profit_p, self.stop_p = self.strategy(price_ie, signal)
            # execute buy or sell orders if hit the price of open, profit, stop loss
            if self.buy_p and self.buy_p[0][0] <= price < self.profit_p:
                self.buy_order(*self.buy_p.pop(0))
            elif self.orders and self.profit_p and price >= self.profit_p:
                self.sell_order(price)
            elif self.orders and self.stop_p and price < self.stop_p:
                self.sell_order(price)
            elif self.orders and signal == (-1 or -2):
                self.sell_order(price)

    def strategy(self, price, signal):
        # only create strategy at a upward trend
        if signal == 1:
            discount = 0
            buy_rate = 0.1
            profit_rate = 1.7
            stop_rate = -0.5
        elif signal == 2:
            discount = 0.3
            buy_rate = 0.0
            profit_rate = 0.7
            stop_rate = -0.3

        try:
            return self.price_range(price, buy_rate, profit_rate, stop_rate, discount)
        except:
            return None, None, None

    def price_range(self, price, buy_rate, profit_rate, stop_rate, discount, split=3):
        # split a buy order into an number of orders
        vols = np.cumsum(range(split))[:0:-1]

        # create different buy prices
        prices = price * (1 + np.arange(buy_rate, profit_rate, (profit_rate - buy_rate ) / float(split)) * self.threshold)

        # total value of order cannot exceed the balance
        ratio = self.balance / (np.sum(vols * prices[:-1]) * (1 - discount))

        price_range = [(p, round(v * ratio) - 1) for p, v in zip(prices, vols)]
        profit_price = price * (1 + profit_rate * self.threshold)
        stop_price = price * (1 + stop_rate * self.threshold)
        return price_range, profit_price, stop_price

    def update_records(self, profit, vol):
        self.profits.append([profit, self.step - 1])

        if profit >= 0:
            self.order_record[0] += 1
            self.volume_record[0] += vol
        else:
            self.order_record[1] += 1
            self.volume_record[1] += vol