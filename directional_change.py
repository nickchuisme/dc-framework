import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from investor import Investor

class FXMarket:

    def __init__(self, threshold=0.005, filepath='./test.csv', test=None, trader=None, fx_pair=None):
        self.data_length = 0
        self.rows = self.load_data(filepath, test)
        self.trader = trader
        self.fx_pair = fx_pair

        self.THRESHOLD = threshold

        self.physic_data = []
        self.event_data = []
        self.signal = []

    def load_data(self, filepath, test):
        # import data and save it into a generator
        with open(filepath) as file:
            if test:
                data = file.readlines()[:test]
            else:
                data = file.readlines()
            self.data_length = len(data)

            for row in data:
                yield row.strip().split(',')

    def data_cleaning(self, row, fx=False):
        time = datetime.strptime(row[0], '%Y%m%d %H%M%S%f')
        price = (float(row[1]) + float(row[2])) / 2

        return time, price

    def update_event_data(self, data, check=3, trade=True):
        # record price and signal info every tick
        self.physic_data.append(data[:2])

        if self.event_data and self.event_data[-1][2] == data[2]:
            self.event_data[-1] = data
        else:
            self.event_data.append(data)

        # Do not trade if signal is not reliable
        if len(self.event_data) >= check and len(set([data[2] for data in self.event_data[-1 * check:]])) < check:
            self.event_data = self.event_data[: -1 * (check - 1)]
            trade = False
        return trade

    def run_market(self):
        # directional change and overshoot framework
        price_ext = None
        price_ie = None
        time_ie = None
        time_duration = 0

        upward = True
        next_signal = 0
        trade = False

        for i, row in enumerate(self.rows):
            time, price = self.data_cleaning(row, fx=True)

            # initialise framework
            if i == 0:
                price_ext = price
                price_ie = price
                time_ie = time
                next_signal = 0
                time_duration = time - time_ie

            elif upward:
                # 1, upward directional change
                if price >= price_ext * (1 + self.THRESHOLD):
                    upward = False
                    price_ext = price
                    price_ie = price
                    time_duration = time - time_ie
                    time_ie = time
                    next_signal = 2

                elif price < price_ext:
                    price_ext = price
                    # -2, downward overshoot
                    if price_ie >= price_ext * (1 + self.THRESHOLD) and time - time_ie > time_duration:
                        price_ie = price
                        time_ie = time
                        next_signal = 1
                    else:
                        next_signal = -2
                else:
                    next_signal = 1

            elif not upward:
                # -1, downward directional change
                if price_ext >= price * (1 + self.THRESHOLD):
                    upward = True
                    price_ext = price
                    price_ie = price
                    time_duration = time - time_ie
                    time_ie = time
                    next_signal = -2
                elif price > price_ext:
                    price_ext = price

                    # 2, upward overshoot
                    if price_ext >= price_ie * (1 + self.THRESHOLD) and time - time_ie > time_duration:
                        price_ie = price
                        time_ie = time
                        next_signal = -1
                    else:
                        next_signal = 2
                else:
                    next_signal = -1
            
            # update info at each intrinsic event and physical time
            trade = self.update_event_data([i, price, next_signal])
            # provide info to trader
            if self.trader:
                self.trader.action(price, price_ie, next_signal, trade)

                if i == self.data_length - 1:
                    self.trader.sell_order(price)

    def plot_result(self, ax=None, label=''):
        try:
            time_p, price_p = np.array(self.physic_data)[:, 0], np.array(self.physic_data)[:, 1]
            time_ie, price_ie, signal = np.array(self.event_data)[:, 0], np.array(self.event_data)[:, 1], np.array(self.event_data)[:, 2]
        except IndexError:
            import sys
            sys.exit(f'Recommend lower dc threshold!! Current Threshold: {self.THRESHOLD}')

        if ax:
            ax.plot(time_p, price_p.ravel(), color='blue', alpha=0.8, linewidth=0.8, label=label)
            ax.plot(time_ie, price_ie.ravel(), color='black', linewidth=0.7)
            ax.plot(time_ie, price_ie.ravel(), 'ro', alpha=0.8, markersize=3.5)
            ax.set_ylabel('Price', fontsize=16)
            ax.set_xticks([])
            ax.set_xlim(0, price_p.size)
        else:
            plt.rcParams["figure.figsize"] = (15, 7)
            plt.plot(time_p, price_p.ravel(), color='blue', alpha=0.8, linewidth=0.8)
            plt.plot(time_ie, price_ie.ravel(), color='black', linewidth=0.7)
            plt.plot(time_ie, price_ie.ravel(), 'ro', alpha=0.8, markersize=3.5)
            plt.xlim(0, price_p.size)
            plt.title(self.fx_pair, fontsize=18)
            plt.xlabel('Time', fontsize=16)
            plt.ylabel('Price', fontsize=16)
            plt.xticks([])

if __name__ == "__main__":

    balance = 10000
    fx_pair_name = 'GBPCHF'
    trader = Investor(threshold= 0.008, balance=balance, fee=3)
    fxmarket = FXMarket(threshold=0.008, filepath='./DAT_ASCII_GBPCHF_T_202203.csv', fx_pair=fx_pair_name, trader=trader)
    fxmarket.run_market()

    profits = np.array(trader.profits)[:, 0]
    profits_idx = np.array(trader.profits)[:, 1]
    profits_fee = np.array(trader.profits_with_fee)[:, 0]
    profits_fee_idx = np.array(trader.profits_with_fee)[:, 1]

    # plot price of physical time, directional change and overshoot
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 7), constrained_layout=True, sharex=True)
    axes = axes.ravel()
    fig.suptitle(f'{fx_pair_name}', fontsize=18)
    fig.supxlabel('Time', fontsize=18)
    fxmarket.plot_result(ax=axes[0])
    axes[1].plot(profits_idx, np.cumsum(profits), label=f'Return(no Fee): {round(np.sum(profits), 3)} {fx_pair_name[:3]} ({(round(np.sum(profits)/balance)*100, 2)}%)')
    axes[1].legend()
    axes[1].plot(profits_fee_idx, np.cumsum(profits_fee), label=f'Return(Fee): {round(np.sum(profits_fee), 3)} {fx_pair_name[:3]} ({round(np.sum(profits_fee)/balance*100, 2)}%)')
    axes[1].legend()
    axes[1].set_ylabel('Return', fontsize=16)
    plt.show()