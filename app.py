import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt
from utils import highlight_rows
import secrets

st.set_page_config(
    page_title="fantrax-golf",
    layout="centered",
    initial_sidebar_state="expanded",
)
alt.themes.enable("dark")

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}

dg_key = st.secrets.dg_key

# GET LIVE GOLF DATA
st.cache_data()
def get_projections():
    live = pd.read_csv(f"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key={dg_key}")
    return live
live = get_projections()
live.rename(columns={'player_name':'player'},inplace=True)

# prep live
names = live['player'].str.split(expand=True)
names[0] = names[0].str.rstrip(",")
names[1] = names[1].str.rstrip(",")
names['player'] = names[1] + " " + names[0]
names['player'] = np.where(names['player']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
names['player'] = np.where(names['player']=='Si Kim', 'Si Woo Kim', names['player'])
names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
live = live.set_index(names.player)

### GET FANTRAX ACTIVE ROSTERS ###
st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk9.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

# prep fantrax
teams.columns = ['player','team','active_reserve']
teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'New Team 4','NT 8':'Sneads Foot','txms':'txmoonshine','MG':'Team Gamble','grrr':'Putt Pirates','[AW]':'AlphaWired'}
teams['team'] = teams.team.map(teams_dict)
teams = teams.loc[teams.active_reserve=='Active'].set_index('player')

### MERGE ACTIVE ROSTERS WITH LIVE SCORING ###
live_merged = pd.merge(teams, live, how='left', left_index=True, right_index=True).fillna(0).sort_values('total')
live_merged['holes_remaining'] = (72 - (live_merged['thru']).fillna(0))
live_merged['holes_remaining'] = np.where(live_merged['position']=='CUT',0,live_merged['holes_remaining']).astype('int')

sidebar_title = st.sidebar.empty()
st.sidebar.markdown("---")
sidebar_phr_table = st.sidebar.empty()

### TEAM FILTER CHARTS ###
team_name = st.sidebar.multiselect(
    label='',
    options=np.array(live_merged['team'].unique()),
    default=np.array(live_merged['team'].unique()))
# st.write("###")
# st.write("###")

# 1 live leaderboard
live_leaderboard = live_merged[['player','team','position','total','round','thru']].fillna(0).sort_values('total')
live_leaderboard[['total','round','thru']] = live_leaderboard[['total','round','thru']].astype('int')
# live_leaderboard = live_leaderboard['total'].replace(to_replace=0,value='E')
live_board = live_leaderboard.copy()
live_leaderboard = (live_leaderboard[live_leaderboard.team.isin(team_name)]
                    .rename(columns={'player':'Player','team':'Team','position':'Pos','total':'Total','round':'Round','thru':'Thru'})
                    .style.apply(highlight_rows, axis=1))

# 2 PHR
live_phr = live_merged[live_merged.team.isin(team_name)].groupby('team')[['total','holes_remaining']].sum().reset_index().rename(columns={'team':'Team','holes_remaining':'PHR'})
live_phr = (live_phr
            .sort_values(by='total')
            .style.apply(highlight_rows, axis=1))

# 3 thru-cut bar
thru_cut_df = live_board[(live_board.position!='CUT') & (live_board.team.isin(team_name))]['team'].value_counts()
thru_cut_bar = px.bar(thru_cut_df,
                 template='presentation',
                 labels={'value':'','index':''},
                 text_auto=True,
                 height=250,
                 log_y=True,
                 title='Players Thru the Cut')
thru_cut_bar.update_layout(showlegend=False,title_x=.25)
thru_cut_bar.update_yaxes(showticklabels=False,showgrid=False)
thru_cut_bar.update_traces(marker_color='rgb(200,200,200)',marker_line_width=1.5, opacity=0.6)

# 4 team score bar
team_score_df = live_board[live_board.team.isin(team_name)].groupby('team')['total'].sum().sort_values()
team_score_bar = px.bar(team_score_df,
                     template='presentation',
                     labels={'value':'','team':''},
                     text_auto=True,
                     height=250,
                     title='Team Score')
team_score_bar.update_layout(showlegend=False,title_x=.33)
team_score_bar.update_yaxes(showticklabels=False,showgrid=False)
team_score_bar.update_traces(marker_color='rgb(200,200,200)',marker_line_width=1.5, opacity=0.6)

# 5 live sg
live_sg = live_merged[live_merged.team.isin(team_name)].groupby('team',as_index=False)[['sg_putt','sg_t2g','sg_total','gir']].mean().reset_index(drop=True)
live_sg = live_sg.style.background_gradient(cmap='Greens').format(precision=2)

### MAIN PAGE ###

# st.plotly_chart(thru_cut_bar, use_container_width=True,config = config)
st.markdown("<h3 style='text-align: center;;'>Live Leaderboard </h3>", unsafe_allow_html=True)
with st.expander('Strokes Gained by Team'):
    st.dataframe(live_sg,height=330,hide_index=True,use_container_width=True)
st.dataframe(live_leaderboard,hide_index=True,height=1750,use_container_width=True, column_config={"Team": None})

### SIDEBAR ###
sidebar_title.markdown("<h2 style='text-align: center;'>Arnold Palmer<br>Invitational </h2>", unsafe_allow_html=True)
sidebar_phr_table.dataframe(live_phr,hide_index=True,use_container_width=True)