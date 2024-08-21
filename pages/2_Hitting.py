import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, date, timedelta
from streamlit_extras.app_logo import add_logo

# Mock data generation
def generate_mock_data(num_players=50, num_days=365):
    players = [f"Player {i}" for i in range(1, num_players + 1)]
    dates = pd.date_range(end=date.today(), periods=num_days)
    data = []
    
    for player in players:
        for d in dates:
            data.append({
                'player': player,
                'date': d,
                'bat_speed': np.random.normal(70, 5),
                'top_8th_ev': np.random.normal(95, 3),
                'gym': np.random.choice(['WA', 'AZ', 'FL', 'Remote'])
            })
    
    return pd.DataFrame(data)

# Time period selection
def select_time_period():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        last_30 = st.button("Last 30 days")
    with col2:
        last_90 = st.button("Last 90 days")
    with col3:
        vs_previous = st.button("vs. Previous Period")
    with col4:
        vs_year = st.button("vs. Previous Year")
    
    end_date = date.today()
    if last_30:
        start_date = end_date - timedelta(days=30)
        selected_period = "Last 30 days"
    elif last_90:
        start_date = end_date - timedelta(days=90)
        selected_period = "Last 90 days"
    elif vs_previous:
        start_date = end_date - timedelta(days=60)
        selected_period = "vs. Previous Period"
    elif vs_year:
        start_date = end_date - timedelta(days=365)
        selected_period = "vs. Previous Year"
    else:
        start_date = end_date - timedelta(days=30)
        selected_period = "Last 30 days"
    
    return start_date, end_date, selected_period

# Hitting Page
def hitting_page(df):
    st.header("Hitting Metrics")
    
    start_date, end_date, selected_period = select_time_period()
    
    gym_type = st.sidebar.multiselect("Select Gym Type", ['in-gym', 'remote'], default=['in-gym', 'remote'])
    
    filtered_df = df[(df['date'] >= pd.Timestamp(start_date)) & 
                     (df['date'] <= pd.Timestamp(end_date))]
    
    if 'in-gym' in gym_type and 'remote' in gym_type:
        gym_filtered_df = filtered_df
    elif 'in-gym' in gym_type:
        gym_filtered_df = filtered_df[filtered_df['gym'] != 'Remote']
    else:
        gym_filtered_df = filtered_df[filtered_df['gym'] == 'Remote']
    
    st.subheader("Bat Speed")
    fig_bat_speed = px.box(gym_filtered_df, x='gym', y='bat_speed', color='gym', 
                           title=f"Bat Speed Distribution by Gym Type ({selected_period})")
    st.plotly_chart(fig_bat_speed)
    
    st.subheader("Top 8th Exit Velocity")
    fig_ev = px.box(gym_filtered_df, x='gym', y='top_8th_ev', color='gym', 
                    title=f"Top 8th Exit Velocity Distribution by Gym Type ({selected_period})")
    st.plotly_chart(fig_ev)
    
    if 'in-gym' in gym_type:
        st.subheader("In-gym Trends")
        in_gym_df = gym_filtered_df[gym_filtered_df['gym'] != 'Remote']
        fig_in_gym = px.line(in_gym_df.groupby('date')[['bat_speed', 'top_8th_ev']].mean().reset_index(), 
                             x='date', y=['bat_speed', 'top_8th_ev'], title="In-gym Hitting Metrics Trend")
        st.plotly_chart(fig_in_gym)
    
    if 'remote' in gym_type:
        st.subheader("Remote Trends")
        remote_df = gym_filtered_df[gym_filtered_df['gym'] == 'Remote']
        fig_remote = px.line(remote_df.groupby('date')[['bat_speed', 'top_8th_ev']].mean().reset_index(), 
                             x='date', y=['bat_speed', 'top_8th_ev'], title="Remote Hitting Metrics Trend")
        st.plotly_chart(fig_remote)

# Main app
def main():
    st.set_page_config(page_title="Hitting Metrics Dashboard", layout="wide")

    # Add additional images to the sidebar
    st.sidebar.image("images/logo.png", caption="Chicks Dig the Long Ball")
    
    st.sidebar.title("Navigation")
    
    # Main content area title
    st.title("Hitting Metrics Dashboard")
    
    # Generate mock data
    df = generate_mock_data()
    
    # Ensure 'date' column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Display the hitting page
    hitting_page(df)

if __name__ == "__main__":
    main()