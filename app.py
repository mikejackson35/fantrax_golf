import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt
from utils import highlight_rows, teams_dict, get_inside_cut, remove_T_from_positions, team_color,fix_names
# import secrets

##### LIBRARY CONFIGs AND SECRETS KEYS #####

st.set_page_config(page_title="fantrax-golf", layout="centered", initial_sidebar_state="expanded")    # streamlit
alt.themes.enable("dark")                                                                             # altair
with open(r"styles/main.css") as f:                                                                   # css
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)    
config = {'displayModeBar': False}                                                                    # plotly

# dg_key = st.secrets.dg_key                                                                         # api keys
dg_key = "e297e933c3ad47d71ec1626c299e"

matchups = {                                    # enter weekly matchups here
    'unit_circle':1,
    'Putt Pirates':2,
    'AlphaWired':3,
    'txmoonshine':2,
    'Sneads Foot':1,
    'New Team 4':4,
    'Team Gamble':4,
    'Philly919':3
}

## LIVE SCORING API ##
path = f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}"

st.cache_data()
def get_live():
    live = round(pd.read_csv(path),2).rename(columns={'player_name':'player'})
    return live
live = get_live()
live = live.set_index(fix_names(live))


## CURRENT WEEK FANTASY ROSTERS & MATCHUPS ##
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fantrax.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams['team'] = teams.team.map(teams_dict)
teams = teams.loc[teams.active_reserve=='Active'].set_index('player')

## MERGE & PROCESS ##
# merge current fantasy teams and live scoring
live_merged = pd.merge(teams, live, how='left', left_index=True, right_index=True)[['team','position','total','round','thru']].fillna(0).sort_values('total')
live_merged = live_merged[live_merged.index != 0].reset_index()
live_merged[['round', 'thru']] = live_merged[['round', 'thru']].astype(int)
# add columns matchup_num & holes_remaining
live_merged['matchup_num'] = live_merged.team.map(matchups)
live_merged['holes_remaining'] = (72 - (live_merged['thru']).fillna(0)).astype(int)
live_merged['holes_remaining'] = np.where(live_merged['position']=='CUT',0,live_merged['holes_remaining']).astype('int')
live_merged['holes_remaining'] = np.where(live_merged['position']=='WD',0,live_merged['holes_remaining']).astype('int')

## SIDEBAR ##
# placeholder for team leaderboard
st.sidebar.markdown("<center>Week 13</center>",unsafe_allow_html=True)
st.sidebar.markdown("---")
sidebar_team_leaderboard = st.sidebar.empty()
# matchup multi-select filter
matchup_num = st.sidebar.multiselect(        
    label='Matchup',
    options=sorted(np.array(live_merged['matchup_num'].unique())),
    default=sorted(np.array(live_merged['matchup_num'].unique())),
)
# data filtered by user
live_merged = live_merged[live_merged.matchup_num.isin(matchup_num)]


## TABLES & CHARTS ##
# team leaderboard
team_leaderboard = (
    live_merged
    [['team','total','holes_remaining','matchup_num']]
    .groupby('team')
    [['total','holes_remaining','matchup_num']]
    .agg({'total':'sum','holes_remaining':'sum','matchup_num':'mean'})
    .convert_dtypes()
)
team_leaderboard = team_leaderboard.sort_values('total').reset_index()
team_leaderboard['team'] = team_leaderboard['team'].astype(str)
team_leaderboard['inside_cut'] = team_leaderboard['team'].map(get_inside_cut(live_merged))
team_leaderboard['total'] = np.where(team_leaderboard['total'] == 0, "E", team_leaderboard['total']).astype(str)
team_leaderboard.columns = ['Team','Total','PHR','Matchup','Inside Cut']
team_leaderboard_bar_df = team_leaderboard.copy()
team_leaderboard = team_leaderboard.style.apply(highlight_rows,axis=1)

# player leaderboard
player_leaderboard = live_merged[['player', 'position', 'total', 'round', 'thru','team','matchup_num']].fillna(0)
player_leaderboard['total'] = np.where(player_leaderboard['total'] == 0, "E", player_leaderboard['total']).astype(str)
player_leaderboard['round'] = np.where(player_leaderboard['round'] == 0, "E", player_leaderboard['round']).astype(str)
player_leaderboard['position'] = np.where(player_leaderboard['position'] == "WAITING", "-", player_leaderboard['position'])
player_leaderboard['thru'] = np.where(player_leaderboard['thru'] == 0, "-", player_leaderboard['thru']).astype(str)
player_leaderboard.columns = ['Player','Pos','Total','Rd','Thru','Team','Matchup']
player_leaderboard = player_leaderboard.style.apply(highlight_rows,axis=1)

# live strokes gained expander
live_merged_strokes_gained = (pd.merge(teams,live,how='left',left_index=True,right_index=True).drop(columns='player').reset_index())
live_merged_strokes_gained = live_merged_strokes_gained.groupby('team',as_index=False)[['sg_putt','sg_arg','sg_app','sg_t2g']].sum().reset_index(drop=True)
live_merged_strokes_gained.columns = ['Team','SG Putt','SG Arg','SG App','SG T2G']
live_merged_strokes_gained = live_merged_strokes_gained.style.background_gradient(cmap='Greens').format(precision=2)

### MAIN PAGE ###
# header
st.markdown("<h3 style='text-align: center;;'>The Valero</h3>", unsafe_allow_html=True)                    
st.markdown("<h5 style='text-align: center;;'>Live Leaderboard</h5>", unsafe_allow_html=True)
# strokes gained expander
with st.expander('Strokes Gained by Team'):                                                                   
    st.dataframe(live_merged_strokes_gained,
                 height=330,hide_index=True,use_container_width=True)
# player leaderboard
st.dataframe(player_leaderboard,                                                                                
             hide_index=True,height=1750,use_container_width=True,
             column_config={"Team": None, "Matchup":None})

### SIDEBAR ###
# team leaderboard
sidebar_team_leaderboard.dataframe(team_leaderboard,                                                                   
                            hide_index=True,use_container_width=True,column_config={"Matchup":None})





## NOT IN USE ##

# CURRENT PLAYERS INSIDE CUT BAR #
# inside_cut_bar = px.bar(
#     team_leaderboard_bar_df,
#     x='Team',
#     y='Inside Cut',
#     text_auto=True,
#     template='plotly_dark',
#     color='Team',
#     color_discrete_map=team_color,
#     labels = {'Team':'Inside Cutline','Inside Cut':''},
#     # title = 'Players Inside Cutline',
#     height = 200,
#     log_y=True).update_traces(marker_color='grey')

# inside_cut_bar.update_layout(
#     showlegend=False,
#     xaxis=dict(showticklabels=True,showgrid=False, tickfont=dict(color='#5A5856', size=13), title_font=dict(color='#5A5856', size=15)),
#     yaxis=dict(showticklabels=False, showgrid=False, tickfont=dict(color='#5A5856', size=13), title_font=dict(color='#5A5856', size=15)),
# )
# CURRENT PLAYERS INSIDE CUT BAR #


# MADE THRU THE CUT BAR #
# thru_cut_df = live_board[(live_board['position'].isin(['CUT', 'WD']) == False) & (live_board['matchup_num'].isin(matchup_num))]['team'].value_counts()
# thru_cut_bar = px.bar(
#     thru_cut_df,
#     template='presentation',
#     labels={'value': '', 'team': ''},
#     text_auto=True,
#     height=250,
#     log_y=True,
#     title='Players Thru Cut')

# thru_cut_bar.update_layout(
#     showlegend=False,
#     title_x=.35,
#     xaxis=dict(showgrid=False, tickfont=dict(color='#5A5856', size=11), title_font=dict(color='#5A5856', size=15)),
#     yaxis=dict(showticklabels=False, showgrid=False))

# thru_cut_bar.update_traces(marker_color='rgb(200,200,200)',marker_line_width=1.5, opacity=0.6)
# MADE THRU THE CUT BAR #