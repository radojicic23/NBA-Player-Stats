import streamlit as st 
import pandas as pd  
import base64
import matplotlib.pyplot as plt 
import seaborn as sns  
import numpy as np 
import lxml

from PIL import Image


image = Image.open("Logo/logo.png")

st.image(image, width=150)

st.title("NBA Player Statistics🏀")

st.sidebar.header("Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1950, 2023))))

# Web scraping of NBA player stats
@st.cache
def load_data(year):
    url = url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == "Age"].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(["Rk"], axis=1)
    return playerstats

player_stats = load_data(selected_year)

#Sidebar - Team selection.
sorted_unique_team = sorted(player_stats.Tm.unique())
selected_team = st.sidebar.multiselect("Team", sorted_unique_team, sorted_unique_team)
    
# Sidebar - Position selection 
unique_positions = ["C", "PF", "SF", "PG", "SG"]
selected_position = st.sidebar.multiselect("Position", unique_positions, unique_positions)

# Filltering data
df_selected_team = player_stats[(player_stats.Tm.isin(selected_team)) & player_stats.Pos.isin(selected_position)]

st.header("Display Player Stats of Selected Team(s)")
st.write("Data Dimensions: " + str(df_selected_team.shape[0]) + " rows and " + str(df_selected_team.shape[1]))
st.dataframe(df_selected_team)

# Download NBA players stats data
def filedownload(df):
    csv = df.to_csv(index=False)
    # string <--> bytes conversion 
    b64 = base64.b64encode(csv.encode()).decode()
    href = f"<a href='data:file/csv;base64,{b64}' download='player_stats.csv'>Download CSV File</a>." 
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap 
if st.button("Intercorrelation Heatmap"):
    st.header("Intercorrelation Matrix Heatmap")
    df_selected_team.to_csv("output.csv", index=False)
    df = pd.read_csv("output.csv")
    
    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.tril_indices_from(mask)] = True 
    with sns.axes_style("darkgrid"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)
    