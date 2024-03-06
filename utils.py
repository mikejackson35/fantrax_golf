import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt

def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#FF99FF' # Pink
    elif value == 'Philly919':
        color = '#7f3c8d' # Purple
    elif value == 'AlphaWired':
        color = '#3969ac' # Blue
    elif value == 'Sneads Foot':
        color = '#f2b701' # Gold
    elif value == 'New Team 4':
        color = '#FF6666' # Magenta
    elif value == 'Team Gamble':
        color = '#e68310' # Orange
    elif value == 'txmoonshine':
        color = '#00868b' # Aqua
    else:
        color = '#a5aa99' # Grey
    return ['background-color: {}'.format(color) for r in row]

def highlight_cols(col):

    if col.team == 'unit_circle':
        color = '#FF99FF' # Pink
    elif col.team == 'Philly919':
        color = '#7f3c8d' # Purple
    elif col.team == 'AlphaWired':
        color = '#3969ac' # Blue
    elif col.team == 'Sneads Foot':
        color = '#f2b701' # Gold
    elif col.team == 'New Team 4':
        color = '#FF6666' # Magenta
    elif col.team == 'Team Gamble':
        color = '#e68310' # Orange
    elif col.team == 'txmoonshine':
        color = '#00868b' # Aqua
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

team_color={
                "Philly919": 'rgb(127,60,141)',
                "unit_cirle": 'rgb(17,165,121)',
                "AlphaWired": 'rgb(57,105,172)',
                "Sneads Foot": 'rgb(242,183,1)',
                "New Team 4": 'rgb(231,63,116)',
                "Team Gamble": 'rgb(230,131,16)',
                "txmoonshine": 'rgb(0,134,139)',
                "Putt Pirates": 'rgb(165,170,153)'}