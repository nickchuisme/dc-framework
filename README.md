# dc-framework
Directional Changes Framework

1. Implement a directional change framework with empirical evidence based on the algorithm according to the literature[1]. I introduce another function to obtain a more accurate point of directional change and the end of overshoot.

2. An investor is designed to fetch information of each tick from the market with enough liquidity and then exploit a strategy. Here are some steps that an investor creates a strategy and trades in the market.

- receive information (price, price of recent intrinsic event, signal)
- create a strategy depending on the price of the intrinsic event
- generate three prices to place long positions, stop profiting, and stop-loss (split the volumes of buy orders into cumulative volumes, e.g. [1, 3, 6, 10])
- submit orders at buy prices and sell orders when arriving at the profiting price and stop loss.
- a trader can submit orders with any volume that assuming the market with enough liquidity.

## Results

GBPCHF (20220301-20220331)

Figure 1: events of directional changes and overshoots

Figure 2: backtesting a strategy by dc framework within/out transaction fee.

<img src="https://imgur.com/BEDNpze.png" width="700" height="500">

## Reference

[1] Petrov, V., Golub, A., & Olsen, R. B. (2018). Agent-Based Model in Directional-Change Intrinsic Time. Available at SSRN 3240456.
