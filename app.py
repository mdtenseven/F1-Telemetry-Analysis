import streamlit as st
import pandas as pd
import numpy as np
import fastf1
import os

# 1. Page Configuration
st.set_page_config(page_title="Ultimate F1 History Engine", page_icon="🏎️", layout="wide")
st.title("🏁 Ultimate F1 Telemetry & Data Engine")
st.write("Select a season year and track to dynamically pull the exact race weekend grid.")

# Data availability notice
st.info(
    "📊 **Data Availability Notice:** Full telemetry streams (Speed, Throttle, Brake, Gear) "
    "are available for the **2018 season onward**. For years prior to 2018, "
    "the FIA did not collect or distribute modern multi-channel sensor arrays, so the app will display "
    "historical classification results instead."
)

# Ensure cache directory exists
if not os.path.exists('fastf1_cache'):
    os.makedirs('fastf1_cache')
fastf1.Cache.enable_cache('fastf1_cache')

# 2. Sidebar Settings: Direct Year Selection
st.sidebar.header("Race Controls")

supported_years = list(range(2026, 1949, -1))
selected_year = st.sidebar.selectbox("Select Season Year", supported_years)

grand_prix_list = [
    "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", 
    "Monaco", "Canada", "Spain", "Austria", "Great Britain", "Hungary", 
    "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore", 
    "United States", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
]
selected_gp = st.sidebar.selectbox("Select Grand Prix", sorted(grand_prix_list))
session_type = st.sidebar.selectbox("Select Session", ["Qualifying", "Race"])

telemetry_channel = st.sidebar.radio(
    "Select Telemetry Channel", 
    ["Speed (km/h)", "Throttle (%)", "Brake (On/Off)", "Gear"]
)

# 3. Dynamic Database Loading & Lineup Syncing
f1_session_type = 'Q' if session_type == "Qualifying" else 'R'

with st.spinner("🔍 Scanning weekend registration logs..."):
    try:
        session = fastf1.get_session(selected_year, selected_gp, f1_session_type)
        session.load(telemetry=False, weather=False, messages=False)
        
        results = session.results
        if not results.empty:
            dynamic_drivers = []
            for _, row in results.iterrows():
                # Streamlined format: 3-letter code + (Team Name)
                label = f"{row['Abbreviation']} ({row['TeamName']})"
                dynamic_drivers.append(label)
            dynamic_drivers.sort()
        else:
            dynamic_drivers = []
            
    except Exception:
        dynamic_drivers = []

# 4. Displaying the Dynamic Options For The Selected Year
st.subheader(f"👥 Official Entry Roster — {selected_year}")
if dynamic_drivers:
    selected_drivers = st.multiselect(
        f"Choose drivers who raced at the {selected_year} {selected_gp} GP:", 
        dynamic_drivers
    )
else:
    st.warning("Could not pull a roster for this specific timeline combination. The race might be in the future, or the server is updating.")
    selected_drivers = []

# 5. Telemetry Analytics Engine
st.subheader(f"📊 {telemetry_channel} Analytics View")

if len(selected_drivers) == 0:
    st.info("Select one or more drivers from the weekend entry list box above to render telemetry comparisons.")
elif selected_year < 2018:
    st.error(f"⚠️ Telemetry sensor line graphs cannot be drawn for {selected_year} because the FIA did not collect multi-channel sensor streams back then. Here are the official weekend session results instead:")
    st.dataframe(results[['Position', 'Abbreviation', 'LastName', 'TeamName', 'GridPosition']].set_index('Position'))
else:
    with st.spinner("⚡ Fetching deep telemetry from the database..."):
        try:
            session.load(telemetry=True, weather=False, messages=False)
            chart_data = pd.DataFrame()
            
            for driver in selected_drivers:
                # Extract the 3-letter abbreviation directly from the start of the text choice
                driver_abc = driver.split(" ")[0]
                
                driver_info = results[results['Abbreviation'] == driver_abc].iloc[0]
                team_verified = driver_info['TeamName']
                legend_label = f"{driver_abc} ({team_verified})"
                
                driver_lap = session.laps.pick_driver(driver_abc).pick_fastest()
                telemetry = driver_lap.get_telemetry()
                
                channel_map = {
                    "Speed (km/h)": "Speed", "Throttle (%)": "Throttle",
                    "Brake (On/Off)": "Brake", "Gear": "Gear"
                }
                db_channel = channel_map[telemetry_channel]
                
                driver_df = pd.DataFrame({
                    'Distance': telemetry['Distance'],
                    legend_label: telemetry[db_channel]
                }).drop_duplicates(subset=['Distance']).set_index('Distance')
                
                if chart_data.empty:
                    chart_data = driver_df
                else:
                    chart_data = chart_data.join(driver_df, how='outer')
            
            chart_data = chart_data.interpolate(method='linear').fillna(method='bfill')
            st.line_chart(chart_data)
            
        except Exception as e:
            st.error(f"Error compiling active telemetry tracks: {e}")
            