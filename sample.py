import streamlit as st
import pandas as pd
import plotly.express as px
import mariadb

# --- DB Connection ---
@st.cache_resource
def connect_to_mariadb():
    try:
        conn = mariadb.connect(
            host="localhost",
            user="root",
            password="",
            database="project",
            port=3306
        )
        return conn
    except mariadb.Error as err:
        st.error(f"Database connection error: {err}")
        return None

@st.cache_data
def load_data():
    conn = connect_to_mariadb()
    query = "SELECT * FROM bird_observations"
    return pd.read_sql(query, conn)

# giving title
st.set_page_config(page_title="Bird Observation EDA", layout="wide")
st.title("🦜 Bird Observation Analysis Dashboard")

df = load_data()

# for sidebars
st.sidebar.header("Filter Data")
admin_unit = st.sidebar.multiselect("Admin Unit", df["Admin_Unit_Code"].dropna().unique())
location_type = st.sidebar.multiselect("Location Type", df["Location_Type"].dropna().unique())
season = st.sidebar.multiselect("Season", df["Season"].dropna().unique())
year = st.sidebar.multiselect("Year", sorted(df["Year"].dropna().unique()))

# Filter Data 
filtered_df = df.copy()
if admin_unit:
    filtered_df = filtered_df[filtered_df["Admin_Unit_Code"].isin(admin_unit)]
if location_type:
    filtered_df = filtered_df[filtered_df["Location_Type"].isin(location_type)]
if season:
    filtered_df = filtered_df[filtered_df["Season"].isin(season)]
if year:
    filtered_df = filtered_df[filtered_df["Year"].isin(year)]

# tabs for easy visualization
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🕒 Temporal & Environment", "🧬 Species Analysis"])

# for tab 1
with tab1:
    st.subheader("1. Top Species Distribution")
    if "Scientific_Name" in filtered_df.columns:
        species_count = filtered_df["Scientific_Name"].value_counts().reset_index()
        species_count.columns = ["Species", "Count"]
        fig_species = px.bar(species_count.head(20), x="Species", y="Count", color="Count",
                             title="Top 20 Observed Species")
        st.plotly_chart(fig_species, use_container_width=True)

    st.subheader("2. Diversity by Location Type")
    if "Scientific_Name" in filtered_df.columns and "Location_Type" in filtered_df.columns:
        loc_species = filtered_df.groupby("Location_Type")["Scientific_Name"].nunique().reset_index()
        loc_species.columns = ["Location_Type", "Unique_Species"]
        fig_div = px.treemap(loc_species, path=["Location_Type"], values="Unique_Species",
                             title="Species Diversity Across Location Types")
        st.plotly_chart(fig_div, use_container_width=True)

# for tab 2
with tab2:
    with st.expander("🔥 Observation Heatmap by Year & Month", expanded=True):
        if "Year" in filtered_df.columns and "Month" in filtered_df.columns:
            heat_data = filtered_df.groupby(["Year", "Month"]).size().reset_index(name="Observations")
            fig_heat = px.density_heatmap(heat_data, x="Month", y="Year", z="Observations",
                                          title="Heatmap of Observations by Month and Year",
                                          color_continuous_scale="Viridis")
            st.plotly_chart(fig_heat, use_container_width=True)

    with st.expander("🕐 Observation Timing"):
        if "Start_Hour" in filtered_df.columns:
            fig_time = px.histogram(filtered_df.dropna(subset=["Start_Hour"]),
                                    x="Start_Hour", nbins=24,
                                    title="Distribution of Start Hour of Observations")
            st.plotly_chart(fig_time, use_container_width=True)

    with st.expander("🌬️ Environmental Impact - Wind Speed"):
        if "Wind_Speed_mph" in filtered_df.columns and "Season" in filtered_df.columns:
            fig_wind = px.box(filtered_df.dropna(subset=["Wind_Speed_mph"]),
                              x="Season", y="Wind_Speed_mph", color="Season",
                              title="Wind Speed Distribution by Season")
            st.plotly_chart(fig_wind, use_container_width=True)

# for tab 3
with tab3:
    st.subheader("Top Observers")
    if "Observer" in filtered_df.columns:
        observer_df = filtered_df["Observer"].value_counts().reset_index()
        observer_df.columns = ["Observer", "Observations"]
        fig_obs = px.bar(observer_df.head(15), x="Observer", y="Observations", color="Observations",
                         title="Top 15 Observers")
        st.plotly_chart(fig_obs, use_container_width=True)

    st.subheader("Species Distribution by Distance")
    if "Distance_Num" in filtered_df.columns:
        fig_dist = px.histogram(filtered_df, x="Distance_Num", nbins=30,
                                title="Distribution of Distance Observed")
        st.plotly_chart(fig_dist, use_container_width=True)


st.markdown("---")
st.info("🔍 Tip: Use sidebar filters to slice data by admin units, years, and habitats.")