import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date, timedelta
from streamlit_extras.app_logo import add_logo

# Mock data generation
def generate_mock_data(num_players=50, num_days=365):
    players = [f"Player {i}" for i in range(1, num_players + 1)]
    end_date = pd.Timestamp.now().floor('D')
    dates = pd.date_range(end=end_date, periods=num_days)
    data = []
    
    for player in players:
        injury_start = np.random.choice(dates, size=np.random.randint(0, 3))
        injury_duration = np.random.randint(7, 60, size=len(injury_start))
        injury_periods = [(start, start + pd.Timedelta(days=int(duration))) for start, duration in zip(injury_start, injury_duration)]
        
        for d in dates:
            is_injured = any(start <= d <= end for start, end in injury_periods)
            gym = np.random.choice(['WA', 'AZ', 'FL', 'Fully Remote'])
            gym_type = 'in-gym' if gym != 'Fully Remote' else 'remote'
            data.append({
                'player': player,
                'date': d,
                'is_injured': is_injured,
                'injury_type': np.random.choice(['Shoulder', 'Elbow', 'Back', 'Knee', 'Ankle']) if is_injured else None,
                'gym': gym,
                'gym_type': gym_type
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

# Injury Tracker Page
def injury_tracker_page(df, gym_type, specific_gym):
    start_date, end_date, selected_period = select_time_period()
    
    filtered_df = df[(df['date'] >= pd.Timestamp(start_date)) & 
                     (df['date'] <= pd.Timestamp(end_date)) &
                     (df['gym_type'].isin(gym_type)) &
                     (df['gym'].isin(specific_gym))]
    
    active_dl = filtered_df[filtered_df['is_injured']].groupby('date')['player'].nunique()
    total_players = filtered_df.groupby('date')['player'].nunique()
    injury_rate = (active_dl / total_players * 100).fillna(0)
    
    st.subheader("Active DL vs Total Players")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=active_dl.index, y=active_dl.values, name="Active DL", mode="lines"))
    fig.add_trace(go.Scatter(x=total_players.index, y=total_players.values, name="Total Players", mode="lines"))
    fig.update_layout(title=f"Active DL vs Total Players ({selected_period})", xaxis_title="Date", yaxis_title="Number of Players")
    st.plotly_chart(fig)
    
    st.subheader("Injury Rate")
    fig_rate = px.line(x=injury_rate.index, y=injury_rate.values, 
                       title=f"Injury Rate ({selected_period})", labels={'x': 'Date', 'y': 'Injury Rate (%)'})
    st.plotly_chart(fig_rate)

    # Additional Injury Tracker analyses
    st.subheader("Injury Type Distribution")
    injury_type_dist = filtered_df[filtered_df['is_injured']]['injury_type'].value_counts()
    fig_injury_type = px.pie(values=injury_type_dist.values, names=injury_type_dist.index, 
                             title="Distribution of Injury Types")
    st.plotly_chart(fig_injury_type)

    st.subheader("Injury Duration")
    injury_durations = []
    for player in filtered_df['player'].unique():
        player_data = filtered_df[filtered_df['player'] == player]['is_injured']
        injury_periods = player_data.ne(player_data.shift()).cumsum()[player_data]
        durations = injury_periods.groupby(injury_periods).size()
        injury_durations.extend(durations.tolist())

    fig_duration = px.histogram(x=injury_durations, nbins=20,
                                title="Distribution of Injury Durations",
                                labels={'x': 'Duration (days)', 'y': 'Count'})
    st.plotly_chart(fig_duration)

    st.subheader("Injury Rate by Gym")
    gym_injury_rate = filtered_df.groupby('gym').apply(lambda x: (x['is_injured'].sum() / len(x)) * 100).sort_values(ascending=False)
    fig_gym_rate = px.bar(x=gym_injury_rate.index, y=gym_injury_rate.values,
                          title="Injury Rate by Gym",
                          labels={'x': 'Gym', 'y': 'Injury Rate (%)'})
    st.plotly_chart(fig_gym_rate)

def main():
    st.set_page_config(page_title="Injury Tracker Dashboard", layout="wide")

    # Add additional images to the sidebar
    st.sidebar.image("images/logo.png", caption="Chicks Dig Availability")
    
    # Add gym type filter
    gym_type = st.sidebar.multiselect("Select Gym Type", ['in-gym', 'remote'], default=['in-gym', 'remote'])
    
    # Add specific gym filter
    specific_gym = st.sidebar.multiselect("Select Specific Gym", ['WA', 'AZ', 'FL', 'Fully Remote'], default=['WA', 'AZ', 'FL', 'Fully Remote'])
    
    # Main content area title
    st.title("Injury Tracker Dashboard")
    
    # Generate mock data
    df = generate_mock_data()
    
    # Display the injury tracker page
    injury_tracker_page(df, gym_type, specific_gym)

if __name__ == "__main__":
    main()