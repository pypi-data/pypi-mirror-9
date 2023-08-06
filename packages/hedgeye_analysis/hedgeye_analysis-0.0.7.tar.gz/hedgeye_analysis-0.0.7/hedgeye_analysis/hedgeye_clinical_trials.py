# -*- coding: utf-8 -*-
"""
HedgeyeClinicalTrials

Created on Fri Feb 20 09:19:42 2015

@author: JLavin
"""

from hedgeye_analysis.hedgeye_analysis_boilerplate import *

def pipe_split(x):
    return str(x).split('|')

def to_yr_month(dateval):
    dateval = pd.to_datetime(dateval)
    try:
        return str(dateval.year) + '-' + str(dateval.month).zfill(2)
    except:
        return ""
    
def month_str_to_yyyy_mm(month_str):
    try:
        return to_yr_month(datetime.datetime.strptime(month_str, "%B %Y"))
    except:
        return ""
    
def all_months(df):
    start_months = set(df['Start Month']) if ('Start Month' in df.columns) else set()
    completion_months = set(df['Completion Month']) if ('Completion Month' in df.columns) else set()
    received_months = set(df['Received Month']) if ('Received Month' in df.columns) else set()
    months = start_months | completion_months | received_months
    return months

def collaborators_count(df):
    collaborators = {}
    for index, row in df[['Sponsor/Collaborators']].iterrows():
        for collab in row['Sponsor/Collaborators']:
            collaborators[collab.strip()] = collaborators.get(collab.strip(), 0) + 1
    return collaborators

def calc_collabs_for_month(df, month_col_name='Completion Month', month_col_value='2015-01'):
    collaborators = {}
    for index, row in trials.loc[trials[month_col_name] == month_col_value].iterrows():
        for collab in row['Sponsor/Collaborators']:
            collaborators[collab.strip()] = collaborators.get(collab.strip(), 0) + 1
    col_name = month_col_name.replace(' Month','') + '-' + month_col_value
    new_collab_df = pd.DataFrame.from_records(sorted(collaborators.items(), key=lambda x: -x[1]), index='Collaborator', columns = ['Collaborator', col_name])
    return df.join(new_collab_df)

def calc_completion_months(df):
    for month in all_months(df):
        df = calc_collabs_for_month(df, 'Completion Month',month)
    return df.reindex_axis(sorted(df.columns), axis=1)

def calc_received_months(df):
    for month in all_months(df):
        df = calc_collabs_for_month(df, 'Received Month',month)
    return df.reindex_axis(sorted(df.columns), axis=1)

def calc_start_months(df):
    for month in all_months(df):
        df = calc_collabs_for_month(df, 'Start Month',month)
    return df.reindex_axis(sorted(df.columns), axis=1)

def data_frame_column_prefix(df):
    """
      Takes df column name like 'Received-2013-02' and returns 'Received'
    """
    import re
    # **** This is failing. I'm not sure why. ****
    return re.sub(r"-.*$", '', df.columns[0])

def plot_collaborator(collaborator, df, start_month='2000-01', end_month='2015-02'):
    date_type = data_frame_column_prefix(df)
    start = date_type + '-' + start_month
    end = date_type + '-' + end_month
    title = date_type + 's for ' + collaborator + ' from ' + start_month + ' to ' + end_month
    series = df.loc[collaborator,start:end]
    series.index = series.index.map(lambda x: x.replace(date_type + '-',''))
    series.plot(title=title, figsize=(8,8))

"""
month_col_name can be 'Completion Month' (the default), 'Start Month' or 'Received Month'
month_col_value should be in 'YYYY-MM' format, like '2015-02' 
"""
def chart_top_collabs_for_month(df, month_col_value='2015-01', num_collaborators=20):
    data_type = data_frame_column_prefix(df)
    col_name = data_type + '-' + month_col_value
    title = "Top " + str(num_collaborators) + " Collaborators for " + data_type + " Month " + month_col_value
    df.ix[:,[col_name]].sort([col_name],ascending=[0]).head(20).plot(kind="bar", figsize=(8,8), title=title)

