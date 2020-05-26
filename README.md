# StockMarketDataMining
Python visualization tools for stock market data.

# Description
usage: show_option_bets.py [-h] stock expiration

Visualize stock option volume. E.g. python show_option_bets.py STOCK EXPIRATION_DATE

positional arguments:

  stock       Stock Ticker. E.g. MSFT, AAPL, etc.

  expiration  Expiration date; required format yyyy-mm-dd. E.g. 2020-06-19.

optional arguments:
  -h, --help  show this help message and exit

# Acknowledgement
We are very grateful to the creators of this project: https://github.com/pydata/pandas-datareader;
This is where we obtained the script to crawl Yahoo for stock option data (options.py).

# Warning
Futures, stocks and options trading involves substantial risk of loss and is not suitable for every investor.
