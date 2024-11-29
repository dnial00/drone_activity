import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import time

# Set the page configuration
st.set_page_config(layout="wide", page_title="Military Drone Dashboard", page_icon=":airplane:")

# Optimized and Cached Data Loading
@st.cache_data
def load_drone_anomalies(path):
    return pd.read_csv(path).head(100)  # Load only the first 100 rows for optimization

# File Paths
drone_anomaly_path = "drone_anomaly_actions.csv"

# Load Data
drone_anomalies = load_drone_anomalies(drone_anomaly_path)

# Map Data Preparation
map_data = drone_anomalies.copy()

# Convert Threat Levels to Numeric Weights for Heatmap
threat_level_weights = {"High": 3, "Medium": 2, "Low": 1}
map_data["weight"] = map_data["threat_level"].map(threat_level_weights)

# Function to Display Videos
def show_video(header, video_url, autoplay=True, muted=False, loop=False):
    disable_hover_css = """
    <style>
    video {
        pointer-events: none; /* Disable all mouse interactions */
        user-select: none;    /* Prevent text selection */
        outline: none;        /* Disable focus outlines */
    }
    </style>
    """
    # Display the custom CSS once
    st.markdown(disable_hover_css, unsafe_allow_html=True)
    st.subheader(header)
    st.video(video_url, autoplay=autoplay, muted=muted, loop=loop)

# Session State Initialization
if "alert_triggered" not in st.session_state:
    st.session_state.alert_triggered = False

if "show_surveillance" not in st.session_state:
    st.session_state.show_surveillance = False

if "coa_selected" not in st.session_state:
    st.session_state.coa_selected = None

# Dashboard Layout
st.title("CTRM Aludra Operations Dashboard")
st.markdown("""
This dashboard provides real-time insights into drone operations, including anomaly detection, 
risk assessment, and executing Courses of Action (COAs) for the Lahad Datu region.
""")

# Layout: Left Panel (Drone Status, Statistics) | Right Panel (Map, COAs, Logs)
left_col, right_col = st.columns([2, 1.5])

# === Left Panel: Drone Status and Statistics ===
with left_col:

    st.header("Drone Activity Status")
    drone_status = pd.DataFrame({
        "Drone ID": ["CTRM Aludra", "CTRM Aludra", "CTRM Aludra", "CTRM Aludra", "CTRM Aludra"],
        "Missions": ["OPS Daulat", "Maritime Surveillance", "OPS Merpati", "OPS Taring", "Border Control Operations"],
        "Status": ["Active", "Active", "Finished", "Finished", "Finished"],
        "Team": ["PASKAU", "No. 22 Skuadron", "Kor Armor Diraja", "PASKAU", "Tentera Darat Udara"],
    })
    st.table(drone_status)

    st.header("Mission Map and Anomalies")

    # Map Layer Toggle
    layer_option = st.radio("Select Map Layer", options=["Heatmap", "Scatterplot"], index=0)

    # Pydeck Map Configuration
    view_state = pdk.ViewState(latitude=5.05, longitude=118.25, zoom=10, pitch=40)

    if layer_option == "Heatmap":
        layer = pdk.Layer(
            "HeatmapLayer",
            data=map_data,
            get_position=["longitude", "latitude"],
            get_weight="weight",  # Use numeric weights
            intensity=10,
            radius_pixels=60,
            threshold=0.2,
        )
    else:  # Scatterplot Layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position=["longitude", "latitude"],
            get_color=[
                "255, 0, 0, 160" if threat_level == "High" 
                else "255, 165, 0, 160" if threat_level == "Medium" 
                else "0, 128, 0, 160" 
                for threat_level in map_data["threat_level"]
            ],
            get_radius=1000,
            pickable=True,
        )

    map_deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": """
                <b>Anomaly Type:</b> {anomaly_type}<br>
                <b>Threat Level:</b> {threat_level}<br>
                <b>Recommended Action:</b> {recommended_action}
            """,
            "style": {"backgroundColor": "steelblue", "color": "white"}
        },
        map_style="mapbox://styles/mapbox/dark-v10",
    )
    st.pydeck_chart(map_deck)

    # === COA Actions and Recommendations(Detailed) ===
    st.header("CTRM Aludra COA & Strategies Selection")

    # COA Data
    coa_data = pd.DataFrame({
        "COA": ["COA 1", "COA 2", "COA 3"],
        "Recommended Action": [
            "Deploy drones to monitor high-threat anomalies.",
            "Coordinate ground units to investigate specific points of interest.",
            "Use electronic warfare to disrupt potential threats."
        ],
        "Execution Time": ["15 mins", "45 mins", "30 mins"],
        "Sucess Rate(%)": ["87.3", "56.2", "78.9"]
    })
    st.table(coa_data)

    # COA Selection
    chosen_coa = st.radio("Choose a COA to execute", options=["COA 1", "COA 2", "COA 3"], index=0)

    # Execution of Selected COA
    if st.button("Execute Selected COA"):
        st.session_state.coa_selected = chosen_coa
        st.session_state.alert_triggered = False  # Reset alert
        st.session_state.show_surveillance = False  # Reset surveillance
        st.success(f"Executing {chosen_coa}: {coa_data.loc[coa_data['COA'] == chosen_coa, 'Recommended Action'].values[0]}")

# === Right Panel: Map, COA Generation, Suspicious Activity Monitoring, and Logs ===
with right_col:
    with st.container(border=True):
        st.header("Statistics and Insights")
        # Resource Consumption Chart
        resource_data = pd.DataFrame({
            "Resource": ["Battery", "Ammunition", "Surveillance Time", "Maintenance Parts", 
            "Fuel/Propellant", "Weapon Systems", "Data Bandwidth", "Sensor Utilization", 
            "Cooling System", "Flight Hours"],
            "Usage": [600, 300, 450, 200, 400, 250, 100, 350, 150, 500]
        })
        resource_chart = px.bar(resource_data, x="Resource", y="Usage", title="Resource Consumption")
        st.plotly_chart(resource_chart, use_container_width=True)

    with st.container(border=True):
        # Probability of Casualties
        casualties_data = pd.DataFrame({
            "Operation Phase": ["Phase 1", "Phase 2", "Phase 3"],
            "Probability (%)": [10, 25, 5]
        })
        casualties_chart = px.line(casualties_data, x="Operation Phase", y="Probability (%)", title="Probability of Casualties")
        st.plotly_chart(casualties_chart, use_container_width=True)

        # === Drone Logs ===
    st.header("CTRM Aludra Logs")
    log_data = [
        {"Timestamp": "2024-11-28 03:01", "Action": "CTRM Aludra deployed to Sector 1-5"},
        {"Timestamp": "2024-11-27 12:10", "Action": "Signal lost for CTRM Aludra"},
        {"Timestamp": "2024-11-27 02:13", "Action": "CTRM Aludra returned to base"},
        {"Timestamp": "2024-11-27 01:40", "Action": "CTRM Aludra deployed to Sector 12-7"},
        {"Timestamp": "2024-11-26 23:56", "Action": "Signal lost for CTRM Aludra"},
        {"Timestamp": "2024-11-14 03:12", "Action": "CTRM Aludra returned to base"},
        {"Timestamp": "2024-11-14 02:30", "Action": "CTRM Aludra deployed to Sector 5-11"},
        {"Timestamp": "2024-11-05 17:20", "Action": "CTRM Aludra signal interupted"},
        {"Timestamp": "2024-10-15 23:55", "Action": "CTRM Aludra returned to base"},
        {"Timestamp": "2024-10-25 23:14", "Action": "Signal lost for CTRM Aludra"},
        {"Timestamp": "2024-10-14 22:53", "Action": "CTRM Aludra deployed to Sector 3-2"}
    ]
    log_df = pd.DataFrame(log_data)
    st.table(log_df)
    

left_col2, right_col2 = st.columns([1, 2])

# === Suspicious Activity Monitoring ===
if st.session_state.get("coa_selected"):

    with left_col2:
        st.header("Drone Activity Monitoring")

        # Show "Normal Operation" video
        show_video("Normal Operation", "https://i.imgur.com/h4ghtfH.mp4", autoplay=True, loop=True)

        # Create a placeholder for the countdown
        countdown_placeholder = st.empty()

        # Simulate monitoring with a countdown
        for remaining_time in range(10, 0, -1):
            countdown_placeholder.info(f"Monitoring Selected Perimeter...")
            time.sleep(1)

        # Trigger alert
        st.session_state.alert_triggered = True

        # Update the placeholder to show the alert
        countdown_placeholder.warning("⚠️ Suspicious activity detected!")

        if st.session_state.alert_triggered:
            if st.button("View Surveillance Video"):
                st.session_state.show_surveillance = True

    with right_col2:
        st.header("")
        with st.container(border = True):
            if st.session_state.show_surveillance:
                # Show surveillance video
                show_video(
                    "Suspicious Activity Detected",
                    "https://i.imgur.com/o64VTM8.mp4",
                    autoplay=True, loop=True
                )
