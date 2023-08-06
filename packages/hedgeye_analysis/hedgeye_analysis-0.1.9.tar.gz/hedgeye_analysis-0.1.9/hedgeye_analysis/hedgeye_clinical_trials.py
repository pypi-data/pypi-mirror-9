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
    
def prepare_trials_df(df):
    df = df[['Sponsor/Collaborators','First Received','Start Date','Completion Date']]
    df['Start Month'] = pd.to_datetime(df['Start Date']).apply(to_yr_month)
    df['Sponsor/Collaborators'] = df[['Sponsor/Collaborators']].applymap(pipe_split)
    df['NumCollaborators'] = df[['Sponsor/Collaborators']].applymap(len)
    df['Completion Month'] = pd.to_datetime(df['Completion Date']).apply(to_yr_month)
    df['Received Month'] = pd.to_datetime(df['First Received']).apply(to_yr_month)
    return df

def df_with_all_months_index(trials_df):
    return pd.DataFrame(index = all_months(trials_df))

def create_collabs_by_month(trials_df):
    by_month = df_with_all_months_index(trials_df)
    collabs_by_month = by_month.join(trials_df.groupby(['Start Month']).sum().rename(columns={'NumCollaborators': 'Collaborators by Start Month'}))
    collabs_by_month = collabs_by_month.join(trials_df.groupby(['Received Month']).sum().rename(columns={'NumCollaborators': 'Collaborators by Received Month'}))
    collabs_by_month = collabs_by_month.join(trials_df.groupby(['Completion Month']).sum().rename(columns={'NumCollaborators': 'Collaborators by Completion Month'}))
    return collabs_by_month.sort().fillna(0)

def all_months(df):
    start_months = set(df['Start Month']) if ('Start Month' in df.columns) else set()
    completion_months = set(df['Completion Month']) if ('Completion Month' in df.columns) else set()
    received_months = set(df['Received Month']) if ('Received Month' in df.columns) else set()
    months = start_months | completion_months | received_months
    months.discard('')
    months.discard('nan-nan')
    return months

def collaborators_count(df):
    collaborators = {}
    for index, row in df[['Sponsor/Collaborators']].iterrows():
        for collab in row['Sponsor/Collaborators']:
            collaborators[collab.strip()] = collaborators.get(collab.strip(), 0) + 1
    return collaborators

def calc_collabs_for_month(trials_df, df, month_col_name='Completion Month', month_col_value=prev_month_year_dash_month_string()):
    collaborators = {}
    for index, row in trials_df.loc[trials_df[month_col_name] == month_col_value].iterrows():
        for collab in row['Sponsor/Collaborators']:
            collaborators[collab.strip()] = collaborators.get(collab.strip(), 0) + 1
    col_name = month_col_value
    new_collab_df = pd.DataFrame.from_records(sorted(collaborators.items(), key=lambda x: -x[1]), index='Collaborator', columns = ['Collaborator', col_name])
    return df.join(new_collab_df)

def calc_completion_months(trials_df, df):
    for month in all_months(trials_df):
        df = calc_collabs_for_month(trials_df, df, 'Completion Month', month)
    return df.fillna(0).reindex_axis(sorted(df.columns), axis=1)

def calc_received_months(trials_df, df):
    for month in all_months(trials_df):
        df = calc_collabs_for_month(trials_df, df, 'Received Month', month)
    return df.fillna(0).reindex_axis(sorted(df.columns), axis=1)

def calc_start_months(trials_df, df):
    for month in all_months(trials_df):
        df = calc_collabs_for_month(trials_df, df, 'Start Month', month)
    return df.fillna(0).reindex_axis(sorted(df.columns), axis=1)

def data_frame_column_prefix(df):
    """
      Takes df column name like 'Received-2013-02' and returns 'Received'
    """
    import re
    # **** This is failing. I'm not sure why. ****
    return re.sub(r"-.*$", '', df.columns[0])

def plot_collaborator(date_type, collaborator, df, start_month='2000-01', end_month=prev_month_year_dash_month_string()):
    # if start_month is not an index value of df, increment start_month and test again
    while start_month not in df:
        start_month = next_month_year_dash_month_string(today = start_month + '-15')
    # if end_month is not an index value of df, decrement end_month and test again
    while end_month not in df:
        end_month = prev_month_year_dash_month_string(today = end_month + '-15')
    title = date_type + 's for ' + collaborator + ' from ' + start_month + ' to ' + end_month
    series = df.loc[collaborator,start_month:end_month]
    series.fillna(0, inplace=True)
    #series.index = series.index.map(lambda x: x.replace(date_type + '-',''))
    series.plot(title=title, figsize=(8,8), ylim = (0, series.max() + 1))

"""
month_col_name can be 'Completion Month' (the default), 'Start Month' or 'Received Month'
month_col_value should be in 'YYYY-MM' format, like '2015-02' 
"""
def chart_top_collabs_for_month(df, month_col_value=prev_month_year_dash_month_string(), num_collaborators=20, date_type=None):
    if date_type:  # should be 'Start,' 'Completion,' or 'Submitted'
      date_type = date_type + ' '
    else:
      date_type = ''
    title = "Top " + str(num_collaborators) + " Collaborators for " + date_type + "Month " + month_col_value
    df.ix[:,[month_col_value]].sort([month_col_value],ascending=[0]).head(20).plot(kind="bar", figsize=(8,8), title=title)

