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
                'expected_velo': np.random.normal(92, 3),
                'gym': np.random.choice(['WA', 'AZ', 'FL', 'Remote']),
                'linear_force': np.random.normal(500, 50),
                'rotational_force': np.random.normal(300, 30),
                'total_force': np.random.normal(800, 80)
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

# High Performance Page
def high_performance_page(df):
    st.header("High Performance Metrics")
    
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
    
    st.subheader("Expected Velo")
    fig_expected_velo = px.box(gym_filtered_df, x='gym', y='expected_velo', color='gym', 
                               title=f"Expected Velo Distribution by Gym Type ({selected_period})")
    st.plotly_chart(fig_expected_velo)
    
    if 'in-gym' in gym_type:
        st.subheader("In-gym Expected Velo Trend")
        in_gym_df = gym_filtered_df[gym_filtered_df['gym'] != 'Remote']
        fig_in_gym = px.line(in_gym_df.groupby('date')['expected_velo'].mean().reset_index(), 
                             x='date', y='expected_velo', title="In-gym Expected Velo Trend")
        st.plotly_chart(fig_in_gym)
    
    if 'remote' in gym_type:
        st.subheader("Remote Expected Velo Trend")
        remote_df = gym_filtered_df[gym_filtered_df['gym'] == 'Remote']
        fig_remote = px.line(remote_df.groupby('date')['expected_velo'].mean().reset_index(), 
                             x='date', y='expected_velo', title="Remote Expected Velo Trend")
        st.plotly_chart(fig_remote)

    # Additional High Performance Metrics
    st.subheader("Player Performance Distribution")
    player_avg = gym_filtered_df.groupby('player')['expected_velo'].mean().reset_index()
    fig_player_dist = px.histogram(player_avg, x='expected_velo', 
                                   title="Distribution of Player Average Expected Velo")
    st.plotly_chart(fig_player_dist)

    # Top Performers
    st.subheader("Top Performers")
    top_players = player_avg.nlargest(10, 'expected_velo')
    fig_top_players = px.bar(top_players, x='player', y='expected_velo', 
                             title="Top 10 Players by Average Expected Velo")
    st.plotly_chart(fig_top_players)

    # Force Change Section
    st.subheader("Force Change Analysis")
    force_type = st.selectbox("Select Force Type", ["Linear Force Change", "Rotational Force Change", "Total Force Change"])

    if force_type == "Linear Force Change":
        force_column = 'linear_force'
        title = "Linear Force Change Over Time"
    elif force_type == "Rotational Force Change":
        force_column = 'rotational_force'
        title = "Rotational Force Change Over Time"
    else:
        force_column = 'total_force'
        title = "Total Force Change Over Time"

    force_df = gym_filtered_df.groupby('date')[force_column].mean().reset_index()
    fig_force = px.line(force_df, x='date', y=force_column, title=title)
    st.plotly_chart(fig_force)

    # Force Distribution
    st.subheader(f"{force_type} Distribution")
    fig_force_dist = px.histogram(gym_filtered_df, x=force_column, 
                                  title=f"Distribution of {force_type}")
    st.plotly_chart(fig_force_dist)

    # Top Performers by Force
    st.subheader(f"Top Performers by {force_type}")
    top_force_players = gym_filtered_df.groupby('player')[force_column].mean().nlargest(10).reset_index()
    fig_top_force = px.bar(top_force_players, x='player', y=force_column, 
                           title=f"Top 10 Players by {force_type}")
    st.plotly_chart(fig_top_force)

# Main app
def main():
    st.set_page_config(page_title="High Performance Metrics Dashboard", layout="wide")

    # Add additional images to the sidebar
    st.sidebar.image("images/logo.png", caption="Chicks Dig Power Ball")
    
    st.sidebar.title("Navigation")
    
    # Main content area title
    st.title("High Performance Metrics Dashboard")
    
    # Generate mock data
    df = generate_mock_data()
    
    # Ensure 'date' column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Display the high performance page
    high_performance_page(df)

if __name__ == "__main__":
    main()