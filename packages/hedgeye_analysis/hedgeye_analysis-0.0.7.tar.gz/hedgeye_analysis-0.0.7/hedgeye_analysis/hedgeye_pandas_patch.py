# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 09:09:21 2015

@author: JLavin
"""

import datetime
import pandas as pd
#import hedgeye_analysis.hedgeye_stock_analysis as sa

def stale_days(self):
    """ Return integer number of calendar days since last observation
        according to dataframe index """
    staleness = datetime.datetime.now() - self.index.to_pydatetime()[-1]
    return staleness.days

pd.DataFrame.stale_days = stale_days

def add_ticker_adj_close(self, ticker):
    """ Add column of Adjusted Close data for ticker to DataFrame """
    stock = globals()['sa'].get_stock(ticker)[['Adj Close']].rename(columns={'Adj Close':ticker})
    #stock = get_stock(ticker)[['Adj Close']].rename(columns={'Adj Close':ticker})
    return self.join(stock)

pd.DataFrame.add_ticker_adj_close = add_ticker_adj_close