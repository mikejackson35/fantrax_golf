import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="fantrax-golf",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
            
[data-baseweb="tab-list"] {
    gap: 4px;
}

[data-baseweb="tab"] {
    height: 30px;
    width: 500px;
    white-space: pre-wrap;
    background-color: #A29F99;
    # background-color: #E8E6E3;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 8px;
    padding-bottom: 8px;
}
            
</style>
        """, unsafe_allow_html=True)

st.cache_data()
def get_projections():
    live = pd.read_csv(r"https://feeds.datagolf.com/preds/live-tournament-stats?stats=sg_putt,sg_arg,sg_app,sg_ott,sg_t2g,sg_bs,sg_total,distance,accuracy,gir,prox_fw,prox_rgh,scrambling&round=event_avg&display=value&file_format=csv&key=e297e933c3ad47d71ec1626c299e")#,usecols=['dk_name','total_points'])
    return live
live = get_projections()
dg_proj_copy = live.copy()
live.rename(columns={'player_name':'player'},inplace=True)

names = live['player'].str.split(expand=True)
names[0] = names[0].str.rstrip(",")
names[1] = names[1].str.rstrip(",")
names['player'] = names[1] + " " + names[0]
names['player'] = np.where(names['player']=='Min Lee', 'Min Woo Lee', names['player'])
names['player'] = np.where(names['player']=='Byeong An', 'Byeong Hun An', names['player'])
names['player'] = np.where(names['player']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
live = live.set_index(names.player)

st.cache_data()
def get_fantrax():
    teams = pd.read_csv(r"fx_wk9.csv",usecols=['Player','Status','Roster Status'])
    return teams
teams = get_fantrax()

teams.columns = ['player','team','active_reserve']
teams_dict = {'919':'Philly919','u_c':'unit_circle','NT 4':'New Team 4','NT 8':'Sneads Foot','txms':'txmoonshine','MG':'Team Gamble','grrr':'Putt Pirates','[AW]':'AlphaWired'}
teams['team'] = teams.team.map(teams_dict)
teams = teams.loc[teams.active_reserve=='Active'].set_index('player')

### opponent inputs ###
current_week = 9

# live look at all 48 active players with player as index
live_merged = pd.merge(teams, live, how='left', left_index=True, right_index=True).fillna(0).sort_values('total')
live_merged_copy = live_merged.copy()
live_merged[['total','round','thru']] = live_merged[['total','round','thru']].astype('int')#.rename(columns={'position':'Pos','total':'Total','round':'Round','thru':'Thru'})

placeholder1 = st.sidebar.empty()
placeholder2 = st.sidebar.empty()
placeholder3 = st.sidebar.empty()
placeholder4 = st.sidebar.empty()
placeholder5 = st.sidebar.empty()

team_name = st.sidebar.multiselect(
    label='Team Filter',
    options=np.array(live_merged['team'].unique()),
    default=np.array(live_merged['team'].unique()),
)

live_merged = live_merged[live_merged['team'].isin(team_name)]

# live_merged = (
#     live_merged
# #     .reset_index()
#     .rename(columns={
#         'player':'Player','team':'Team','position':'Pos','total':'Total','round':'Round','thru':'Thru Cut'}
#            )
# )

def highlight_rows(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#FFCCE5' # Pink
    elif value == 'Philly919':
        color = '#7f3c8d' # Purple
    elif value == 'AlphaWired':
        color = '#3969ac' # Blue
    elif value == 'Sneads Foot':
        color = '#f2b701' # Gold
    elif value == 'New Team 4':
        color = '#e73f74' # Magenta
    elif value == 'Team Gamble':
        color = '#e68310' # Orange
    elif value == 'txmoonshine':
        color = '#00868b' # Aqua
    else:
        color = '#a5aa99' # Grey
    return ['background-color: {}'.format(color) for r in row]

def highlight_rows2(row):
    value = row.loc['Team']
    if value == 'unit_circle':
        color = '#FFCCE5' # Pink
        opacity = 0.25
    elif value == 'Philly919':
        color = '#7f3c8d' # Purple
        opacity = 0.25
    elif value == 'AlphaWired':
        color = '#3969ac' # Blue
        opacity = 0.25
    elif value == 'Sneads Foot':
        color = '#f2b701' # Gold
        opacity = 0.25
    elif value == 'New Team 4':
        color = '#e73f74' # Magenta
        opacity = 0.25
    elif value == 'Team Gamble':
        color = '#e68310' # Orange
        opacity = 0.25
    elif value == 'txmoonshine':
        color = '#00868b' # Aqua
        opacity = 0.25
    else:
        color = '#a5aa99' # Grey
        opacity = 0.25
    return ['background-color: {}; opacity: {}'.format(color,opacity) for r in row]


live_merged['holes_remaining'] = (72 - (live_merged['thru']).fillna(0))
live_merged['holes_remaining'] = np.where(live_merged['position']=='CUT',0,live_merged['holes_remaining']).astype('int')

team_score = live_merged.groupby('team')[['total']].sum()

thru_cut = pd.DataFrame(live_merged[live_merged.position !='CUT']['team'].value_counts())

df_holes_remaining = pd.DataFrame(live_merged.groupby('team')['holes_remaining'].sum())

table = pd.merge(thru_cut,df_holes_remaining, left_index=True, right_index=True)
table = table.merge(team_score, left_index=True, right_index=True).reset_index().rename(columns={'count':'Thru Cut','team':'Team','holes_remaining':'Holes Remaining','total':'Team Score'}).drop(columns='Holes Remaining')


# table showing holes_remaining
def highlight_cols(col):
    # value = col.
    if col.team == 'unit_circle':
        color = '#FFCCE5' # Pink
    elif col.team == 'Philly919':
        color = '#7f3c8d' # Purple
    elif col.team == 'AlphaWired':
        color = '#3969ac' # Blue
    elif col.team == 'Sneads Foot':
        color = '#f2b701' # Gold
    elif col.team == 'New Team 4':
        color = '#e73f74' # Magenta
    elif col.team == 'Team Gamble':
        color = '#e68310' # Orange
    elif col.team == 'txmoonshine':
        color = '#00868b' # Aqua
    else:
        color = '#a5aa99' # Grey
    return ['background-color: {}'.format(color) for c in col]

df_holes_remaining = live_merged.groupby('team',as_index=False)['holes_remaining'].sum()#.sort_values(by='holes_remaining',ascending=False)
df_holes_remaining = df_holes_remaining.T#.set_index('team').T

live_merged = live_merged[['player','team','position','total','round','thru']].rename(columns={'player':'Player','team':'Team','position':'Pos','total':'Total','round':'Rnd','thru':'Thru'}).style.apply(highlight_rows, axis=1)

placeholder1.caption("Week 9")
placeholder2.title('Arnold Palmer Invitational')
placeholder3.markdown("###")
placeholder4.markdown("###")
placeholder5.dataframe(table.sort_values(by='Team Score'),hide_index=True,use_container_width=True)
st.markdown("###")
st.markdown("###")
st.subheader('HOLES REMAINING')
st.dataframe(df_holes_remaining.style.hide(axis=1).apply(highlight_cols, axis=0),hide_index=True,use_container_width=True)
st.markdown("###")
st.markdown("###")
st.subheader('LEADERBOARD')
st.dataframe(live_merged,hide_index=True,height=1800,use_container_width=True)





    