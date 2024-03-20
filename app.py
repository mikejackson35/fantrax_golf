import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt
from utils import highlight_rows, teams_dict
# import secrets

##### LIBRARY CONFIGs AND SECRETS KEYS #####

st.set_page_config(page_title="fantrax-golf", layout="centered", initial_sidebar_state="expanded")    # streamlit
alt.themes.enable("dark")                                                                             # altair
with open(r"styles/main.css") as f:                                                                   # css
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)    
config = {'displayModeBar': False}                                                                    # plotly

dg_key = st.secrets.dg_key                                                                            # api keys


##### GET LIVE GOLF DATA - prep and clean #####

st.cache_data()
def get_projections():
    live = pd.read_csv(f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}")
    return live
live = get_projections()
live.rename(columns={'player_name':'player'},inplace=True)

names = live['player'].str.split(expand=True)                                                           # reverse last/first name
names[0] = names[0].str.rstrip(",")                                                                   
names[1] = names[1].str.rstrip(",")
names['player'] = names[1] + " " + names[0]
names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])                    #fix player names to match fantrax
names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
live = live.set_index(names.player)


##### GET FANTRAX ACTIVE ROSTERS - prep and clean #####

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fantrax.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

matchups = {                                    # enter weekly matchups here
    'unit_circle':1,
    'Putt Pirates':1,
    'AlphaWired':2,
    'txmoonshine':2,
    'Sneads Foot':3,
    'New Team 4':3,
    'Team Gamble':4,
    'Philly919':4
}

teams.columns = ['player','team','active_reserve']
# teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'New Team 4','NT 8':'Sneads Foot','txms':'txmoonshine','MG':'Team Gamble','grrr':'Putt Pirates','[AW]':'AlphaWired'}
teams['team'] = teams.team.map(teams_dict)
teams = teams.loc[teams.active_reserve=='Active'].set_index('player')


#####  MERGE FANTRAX ACTIVE ROSTERS WITH DATAGOLF LIVE SCORING  #####

live_merged = pd.merge(teams, live, how='left', left_index=True, right_index=True).fillna(0).sort_values('total')
live_merged['holes_remaining'] = (72 - (live_merged['thru']).fillna(0))
live_merged['holes_remaining'] = np.where(live_merged['position']=='CUT',0,live_merged['holes_remaining']).astype('int')
live_merged['holes_remaining'] = np.where(live_merged['position']=='WD',0,live_merged['holes_remaining']).astype('int')
live_merged['matchup_num'] = live_merged.team.map(matchups)


#####  SIDEBAR  #####

sidebar_title = st.sidebar.empty()                                      # placeholder - title
st.sidebar.markdown("---")
sidebar_phr_table = st.sidebar.empty()                                  # placeholder - phr table
sidebar_thru_cut_bar = st.sidebar.empty()                               # placeholder - thru cut bar
matchup_num = st.sidebar.multiselect(                                   # matchup filter
    label='Matchup',
    options=sorted(np.array(live_merged['matchup_num'].unique())),
    default=sorted(np.array(live_merged['matchup_num'].unique())),
)


#####  MAKE TABLES AND CHARTS  #####

#1 LIVE LEADERBOARD
live_leaderboard = live_merged[['player', 'team', 'position', 'total', 'round', 'thru', 'matchup_num']].fillna(0).sort_values('total')
live_leaderboard[['total', 'round', 'thru', 'matchup_num']] = live_leaderboard[['total', 'round', 'thru', 'matchup_num']].astype(int)

live_leaderboard['total'] = np.where(live_leaderboard['total'] == 0, "E", live_leaderboard['total']).astype(str)
live_leaderboard['round'] = np.where(live_leaderboard['round'] == 0, "E", live_leaderboard['round']).astype(str)
live_leaderboard['position'] = np.where(live_leaderboard['position'] == "WAITING", "-", live_leaderboard['position'])
live_leaderboard['thru'] = np.where(live_leaderboard['thru'] == 0, "-", live_leaderboard['thru']).astype(str)

live_board = live_leaderboard.copy()
live_leaderboard = (
    live_leaderboard[live_leaderboard.matchup_num.isin(matchup_num)]
    .rename(columns={'player': 'Player', 'team': 'Team', 'position': 'Pos', 'total': 'Total', 'round': 'Round', 'thru': 'Thru', 'matchup_num': 'Matchup'})
    .style.apply(highlight_rows, axis=1)
)

# 2 PLAYER HOLES REMAINING TABLE
live_phr = live_merged[live_merged.matchup_num.isin(matchup_num)].groupby('team').agg({'total': 'sum', 'holes_remaining': 'sum'}).reset_index()
live_phr.rename(columns={'team': 'Team', 'total': 'Total', 'holes_remaining': 'PHR'}, inplace=True)
live_phr.sort_values(by='Total', inplace=True)
live_phr['Total'] = live_phr['Total'].replace(0, 'E')
live_phr['PHR'] = live_phr['PHR'].replace(0, '0')
live_phr = live_phr.style.apply(highlight_rows, axis=1)

# 3 THRU CUT BAR
thru_cut_df = live_board[(live_board['position'].isin(['CUT', 'WD']) == False) & (live_board['matchup_num'].isin(matchup_num))]['team'].value_counts()
thru_cut_bar = px.bar(
    thru_cut_df,
    template='presentation',
    labels={'value': '', 'team': ''},
    text_auto=True,
    height=250,
    log_y=True,
    title='Players Thru Cut'
)

thru_cut_bar.update_layout(
    showlegend=False,
    title_x=.35,
    xaxis=dict(showgrid=False, tickfont=dict(color='#5A5856', size=11), title_font=dict(color='#5A5856', size=15)),
    yaxis=dict(showticklabels=False, showgrid=False)
)

thru_cut_bar.update_traces(marker_color='rgb(200,200,200)',marker_line_width=1.5, opacity=0.6)

# 4 LIVE STROKES GAINED TABLE
live_sg = live_merged.groupby('team',as_index=False)[['sg_putt','sg_arg','sg_app','sg_t2g']].sum().reset_index(drop=True)
live_sg.columns = ['Team','SG Putt','SG Arg','SG App','SG T2G']
live_sg = live_sg.style.background_gradient(cmap='Greens').format(precision=2)

#################
### MAIN PAGE ###
st.markdown("<h3 style='text-align: center;;'>Live Leaderboard</h3>", unsafe_allow_html=True)
with st.expander('Strokes Gained by Team'):
    st.dataframe(live_sg,height=330,hide_index=True,use_container_width=True)
st.dataframe(live_leaderboard,hide_index=True,height=1750,use_container_width=True, column_config={"Team": None, "Matchup":None})

### SIDEBAR ###
sidebar_title.markdown("<h2 style='text-align: center;'>Valspar<br>Championship<br><small>Week 11</small></h2>", unsafe_allow_html=True)
# sidebar_thru_cut_bar.plotly_chart(thru_cut_bar, use_container_width=True,config = config)
sidebar_phr_table.dataframe(live_phr,hide_index=True,use_container_width=True)
