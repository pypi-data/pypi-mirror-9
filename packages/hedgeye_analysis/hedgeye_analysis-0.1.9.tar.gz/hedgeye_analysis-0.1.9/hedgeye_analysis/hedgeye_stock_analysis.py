# -*- coding: utf-8 -*-
"""
HedgeyeStockAnalysis
"""

from hedgeye_analysis.hedgeye_analysis_boilerplate import *
#import hedgeye_analysis.hedgeye_pandas_patch

import pandas.io.data as web

def savedir(source):
  return globals()["{}_savedir".format(source)]()

def default_savedir():
  """ Default directory for saving data """
  return shared_dir() + '/data'

def yahoo_savedir():
  """ Default directory for saving data downloaded from Yahoo """
  return shared_dir() + '/data/yahoo'

def fred_savedir():
  """ Default directory for saving data downloaded from FRED """
  return shared_dir() + '/data/fred'

def google_savedir():
  """ Default directory for saving data downloaded from Google """
  return shared_dir() + '/data/google'

""" 
    Takes list of stock dictionaries, like:
        stocks = [{'df_name': 'aal_close',        'ticker': 'AAL'},
                  {'df_name': 'vix_close',        'ticker': '%5EVIX'},
                  {'df_name': 'gold_close',       'ticker': 'GLD'},
                  {'df_name': 'oil_close',        'ticker': 'OIL'},
                  {'df_name': 'gas_close',        'ticker': 'GASPRICE',     'source': 'fred'},
                  {'df_name': 'gcgas_close',      'ticker': 'DGASUSGULF',   'source': 'fred'}]
    where `ticker` is the name of the variable to download,
          `df_name` is the variable the dataframe will be assigned to, and
          `source` is the (optional) data source (by default: 'yahoo')
    For each stock in stocks, runs something like:
        `aal_close = sa.get_stock_close('AAL', source = 'fred')`
    which downloads data from the source, saves it to a CSV file
    in the shared directory, then saves the closing values in the
    `aal_close` variable.
"""
def download_stocks(stocks):
    for index, stock in enumerate(stocks):
        if 'source' in stock.keys():
            exec(stock['df_name'] + " = sa.get_stock_close('" + stock['ticker'] + "', source = '" + stock['source'] + "')")
        else:
            exec(stock['df_name'] + " = sa.get_stock_close('" + stock['ticker'] + "')")

def plot_two_stock_returns(tickers_or_returns_df, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, **kwargs):
  """ Correlation plot of stock returns for the first two tickers (or DataFrame columns) """
  if end is None:
    end = yesterday() 
  returns = _tickers_to_returns_df(tickers_or_returns_df, **kwargs).iloc[:,0:2]
  ax = returns.plot(kind='scatter', x=returns.columns.values[0], y=returns.columns.values[1], alpha=0.1, **kwargs)
  ax.set_xlabel(returns.columns.values[0])
  ax.set_ylabel(returns.columns.values[1])

def plot_prices(tickers_or_prices_df, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, **kwargs):
  """ Plot of stock prices for the first two tickers (or DataFrame columns) """
  if end is None:
    end = yesterday() 
  prices = _tickers_to_adj_close_df(tickers_or_prices_df, **kwargs)
  ax = prices.plot(subplots=True, figsize=(15,1.5*np.shape(prices)[1]), **kwargs)

def plot_returns(tickers_or_returns_df, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, **kwargs):
  """ Plot of stock returns for the first two tickers (or DataFrame columns) """
  if end is None:
    end = yesterday() 
  returns = _tickers_to_returns_df(tickers_or_returns_df, **kwargs)
  ax = returns.plot(subplots=True, figsize=(15,1.5*np.shape(returns)[1]), **kwargs)

def plot_stock_and_volume():
    import urllib
    import time
    import datetime
    import matplotlib.ticker as mticker
    import matplotlib.dates as mdates

def _tickers_to_returns_df(tickers, **kwargs):
  if isinstance(tickers, pd.DataFrame):
    return tickers
  else:
    return returns_df(tickers, **kwargs)

def _tickers_to_adj_close_df(tickers, **kwargs):
  if isinstance(tickers, pd.DataFrame):
    return tickers
  else:
    return adjusted_close_df(tickers, **kwargs)

def reload():
    pass

def load_stock_from_csv(ticker, savefile, source):
    print("Loading stock {} from CSV file".format(ticker))
    return globals()['__read_stock_from_%s' % source](ticker, savefile)

def download_stock_from_source(ticker, savefile, start, end, source):
    print("Downloading stock {} from {}".format(ticker, source))
    return globals()['__get_stock_from_%s' % source](ticker, savefile, start, end)

def get_stock(ticker, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, reload_after_days=2):
    """ Download (or read from file) stock data for ticker, save it, and return it 
        reload = True forces the data to be downloaded, even if it's up-to-date
        reload_after_days specifies how many days prior to today the last observation can be before it will auto-reload """
    if end is None:
        end = yesterday() 
    savefile = savedir(source) + '/' + ticker.upper() + '.csv'
    if (not reload) and file_exists(savefile):
        stock_data = load_stock_from_csv(ticker, savefile, source)
        # ideally, this method would know about weekends and bank holidays
        if stock_data.stale_days() < reload_after_days:
            return stock_data
        else:
            print("Data too stale. Re-downloading...")
            return download_stock_from_source(ticker, savefile, start, end, source)
    else:
        return download_stock_from_source(ticker, savefile, start, end, source)

def get_stock_close(ticker, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, reload_after_days=2):
    """ Download (or read from file) stock data for ticker, save it, and return just the Adjusted Close """
    df = get_stock(ticker, start, end, source, reload, reload_after_days)
    if source == 'yahoo':
        return df['Adj Close']
    elif source == 'fred':
        return df[ticker]
    else:
        raise "#get_stock_close not yet implemented for {}".format(source)

def add_stock_to_df(ticker, df):
    """ Add column of Adjusted Close data for ticker to DataFrame """
    stock = get_stock(ticker)[['Adj Close']].rename(columns={'Adj Close':ticker})
    return df.join(stock)

def returns_df(tickers, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False, **kwargs):
  """ Build DataFrame with one column of %Chg(Close) data per ticker in tickers """
  if end is None:
    end = yesterday() 
  for ticker in tickers:
    tmp = get_stock(ticker, start=start, end=end, source=source, reload=reload)
    stock = pd.DataFrame(tmp['PctChg'])
    stock.columns = [ticker]
    if 'stock_returns' in locals():
      stock_returns = stock_returns.join(stock)    
    else:
      stock_returns = stock
  return stock_returns.dropna()

def adjusted_close_df(tickers, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False):
  """ Build DataFrame with one column of %Chg(Adjusted Close) data per ticker in tickers """
  if end is None:
    end = yesterday() 
  for ticker in tickers:
    tmp = get_stock(ticker, start=start, end=end, source=source, reload=reload)
    stock = pd.DataFrame(tmp['Adj Close'])
    stock.columns = [ticker]
    if 'stock_returns' in locals():
      stock_returns = stock_returns.join(stock)    
    else:
      stock_returns = stock
  return stock_returns

def get_stocks(tickers, start=datetime.datetime(1980,1,1), end=None, source='yahoo', reload=False):
  """ Download stock data for each stock ticker in tickers """
  if end is None:
    end = yesterday() 
  for ticker in tickers:
    get_stock(ticker, start=start, end=end, source=source, reload=reload)

def __read_stock_from_yahoo(ticker, savefile):
  return pd.read_csv(savefile, index_col = 'Date', parse_dates = True)

def __read_stock_from_google(ticker, savefile):
    print("Called with savefile ", savefile)
    return pd.read_csv(savefile, index_col = 'Date', parse_dates = True)

def __read_stock_from_fred(ticker, savefile):
  return pd.read_csv(savefile, index_col = 'DATE', parse_dates = True)

def __read_stock_close_from_yahoo(ticker, savefile):
  tmp = pd.read_csv(savefile, index_col = 'Date', parse_dates = True)
  return tmp['Adj Close']

def __read_stock_close_from_fred(ticker, savefile):
  tmp = pd.read_csv(savefile, index_col = 'DATE', parse_dates = True)
  return tmp[ticker]

def __get_stock_from_yahoo(ticker, savefile, start, end):
  # http://pandas.pydata.org/pandas-docs/stable/remote_data.html
  data = web.DataReader(ticker, 'yahoo', start, end)
  data['PctChg'] = data['Adj Close'].pct_change()
  data.to_csv(savefile)
  return data

def __get_stock_from_google(ticker, savefile, start, end):
  # http://pandas.pydata.org/pandas-docs/stable/remote_data.html
  data = web.DataReader(ticker, 'google', start, end)
  data['PctChg'] = data['Close'].pct_change()
  data.to_csv(savefile)
  return data

def __get_stock_from_fred(series, savefile, start, end):
  # http://pandas.pydata.org/pandas-docs/stable/remote_data.html
  data = web.DataReader(series, 'fred', start, end)
  # Should do something like the following:
  #data['PctChg'] = data['Adj Close'].pct_change()
  data.to_csv(savefile)
  return data

def __get_stock_close_from_yahoo(ticker, savefile, start, end):
  # http://pandas.pydata.org/pandas-docs/stable/remote_data.html
  data = web.DataReader(ticker, 'yahoo', start, end)
  data['PctChg'] = data['Adj Close'].pct_change()
  data.to_csv(savefile)
  return data['Adj Close']

def __get_stock_close_from_fred(series, savefile, start, end):
  # http://pandas.pydata.org/pandas-docs/stable/remote_data.html
  data = web.DataReader(series, 'fred', start, end)
  # Should do something like the following:
  #data['PctChg'] = data['Adj Close'].pct_change()
  data.to_csv(savefile)
  return data[series]
