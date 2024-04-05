import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt

team_color={
     "Philly919": 'rgb(14,195,210)',
     "unit_circle": 'rgb(194,139,221)',
     "AlphaWired": 'rgb(247,160,93)',
     "Sneads Foot": 'rgb(70,214,113)',
     "New Team 4": 'rgb(247,94,56)',
     "Team Gamble": 'rgb(38,147,190)',
     "txmoonshine": 'rgb(219,197,48)',
     "Putt Pirates": 'rgb(115,112,106)'
     }

active_color={
    "Active":'rgb(146,146,143)',
    "Reserve":'rgb(220,222,202)'
    }

teams_dict = {
        '919':'Philly919',
        'u_c':'unit_circle',
        'NT 4':'New Team 4',
        'NT 8':'Sneads Foot',
        'txms':'txmoonshine',
        'MG':'Team Gamble',
        'grrr':'Putt Pirates',
        '[AW]':'AlphaWired'
        }

stats_dict = {
    'bb_ratio':'Birdie Bogey Ratio',
    'bird_num':'Num of Birdies',
    'median_delta':'+/- Weekly Median',
    'total_pts':'Fantasy Points',
    'plc_pts':'Place Points',
    'cuts_made':'Avg Cuts Made/Wk',
    'pp_hole':'Points per Hole Played',
    'pars_num':'Num of Pars',
    'eag_num':'Num of Eagles',
    'dbog_num':'Num of Double Bogeys',
    'bog_num':'Num of Bogeys'
}

def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#c28bdd' # Purple
    elif value == 'Philly919':
        color = '#0ec3d2' # Aqua
    elif value == 'AlphaWired':
        color = '#f7a05d' # Orange
    elif value == 'Sneads Foot':
        color = '#46d671' # Green
    elif value == 'New Team 4':
        color = '#f75e38' # Red
    elif value == 'Team Gamble':
        color = '#2693be' # Navy
    elif value == 'txmoonshine':
        color = '#dbc530' # Yellow
    else:
        color = '#73706a' # Grey
    return ['background-color: {}'.format(color) for r in row]

def plus_prefix(a):
    if a > 0:
        b = f"+{a}"
    else:
        b = a
    return b

def highlight_rows_team_short(row):
    value = row.loc['Team']
    if value == 'u_c':
        color = '#c28bdd' # Purple
    elif value == '919':
        color = '#0ec3d2' # Aqua
    elif value == '[AW]':
        color = '#f7a05d' # Orange
    elif value == 'NT 8':
        color = '#46d671' # Green
    elif value == 'NT 4':
        color = '#f75e38' # Red
    elif value == 'MG':
        color = '#2693be' # Navy
    elif value == 'txms':
        color = '#dbc530' # Yellow
    else:
        color = '#73706a' # Grey
    return ['background-color: {}'.format(color) for r in row]

def highlight_cols(col):

    if col.team == 'unit_circle':
        color = '#FF99FF' # Purple
    elif col.team == 'Philly919':
        color = '#7f3c8d' # Aqua
    elif col.team == 'AlphaWired':
        color = '#3969ac' # Orange
    elif col.team == 'Sneads Foot':
        color = '#f2b701' # Green
    elif col.team == 'New Team 4':
        color = '#FF6666' # Red
    elif col.team == 'Team Gamble':
        color = '#e68310' # Navy
    elif col.team == 'txmoonshine':
        color = '#00868b' # Yellow
    else:
        color = '#a5aa99' # Grey
    return ['background-color: {}'.format(color) for c in col]

def get_active_rosters(teams):
    '''
    takes in fantrax weekly download and returns a table of active rosters
    with team names as column labels
    '''
    active_rosters = []
    for team in teams.team.unique():
        one_roster = teams.loc[(teams.team==team) & (teams.active_reserve=='Active')].index
        active_rosters.append(one_roster)
        
    cols = teams.team.unique()
    active_rosters = pd.DataFrame(active_rosters, index=cols).T
    return active_rosters

def remove_T_from_positions(dataframe):
    """
    Remove 'T' from positions in a given column of a DataFrame.

    Parameters:
        dataframe (pandas.DataFrame): DataFrame containing the data.
        column_name (str): Name of the column containing positions.

    Returns:
        pandas.DataFrame: DataFrame with 'T' removed from positions in the specified column.
    """
    dataframe['position'] = dataframe['position'].str.replace('T', '')
    return dataframe

def get_inside_cut(live_merged):
    """
    Filter DataFrame based on position threshold and group by team.

    Parameters:
        dataframe (pandas.DataFrame): DataFrame containing the data.
        position_threshold (str): Threshold position for filtering.

    Returns:
        pandas.DataFrame: DataFrame with filtered data grouped by team.
    """
    live_merged = live_merged[live_merged['position'] != "WAITING"]
    live_merged = remove_T_from_positions(live_merged)
    live_merged['position'] = live_merged['position'].astype('int')
    inside_cut_df = pd.DataFrame(live_merged[live_merged['position'] < 66].team.value_counts()).reset_index()
    inside_cut_df.columns = ['team','inside_cut']
    
    inside_cut_dict = dict(inside_cut_df.values)
    return inside_cut_dict

def fix_names(dg_live):
    """
    Takes in live datagolf scoring, cleans names, outputs list of active players this week
    """
    names = dg_live['player'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player'] = names[1] + " " + names[0]

    names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
    names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])
    names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
    names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
    names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
    names['player'] = np.where(names['player']=='Vince Whaley', 'Vincent Whaley', names['player'])
    names['player'] = np.where(names['player']=='Kevin Yu', 'kevin Yu', names['player'])
    names['player'] = np.where(names['player']=='Kyounghoon Lee', 'Kyoung-Hoon Lee', names['player'])
    return names.player

