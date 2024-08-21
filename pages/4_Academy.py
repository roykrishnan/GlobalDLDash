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
                'throwing_velo': np.random.normal(85, 5),
                'bat_speed': np.random.normal(70, 5),
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

# Academy Page
def academy_page(df):
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
    
    metrics = ['expected_velo', 'throwing_velo', 'bat_speed']
    
    for metric in metrics:
        st.subheader(f"{metric.replace('_', ' ').title()}")
        fig = px.box(gym_filtered_df, x='gym', y=metric, color='gym', 
                     title=f"{metric.replace('_', ' ').title()} Distribution by Gym Type ({selected_period})")
        st.plotly_chart(fig)
    
    if 'in-gym' in gym_type:
        st.subheader("In-gym Trends")
        in_gym_df = gym_filtered_df[gym_filtered_df['gym'] != 'Remote']
        fig_in_gym = px.line(in_gym_df.groupby('date')[metrics].mean().reset_index(), 
                             x='date', y=metrics, title="In-gym Metrics Trend")
        st.plotly_chart(fig_in_gym)
    
    if 'remote' in gym_type:
        st.subheader("Remote Trends")
        remote_df = gym_filtered_df[gym_filtered_df['gym'] == 'Remote']
        fig_remote = px.line(remote_df.groupby('date')[metrics].mean().reset_index(), 
                             x='date', y=metrics, title="Remote Metrics Trend")
        st.plotly_chart(fig_remote)

    # Player Progress
    st.subheader("Player Progress")
    player_progress = gym_filtered_df.groupby('player')[metrics].agg(['first', 'last', 'mean'])
    player_progress['improvement'] = (player_progress['expected_velo']['last'] - player_progress['expected_velo']['first']) / player_progress['expected_velo']['first'] * 100
    top_improvers = player_progress.nlargest(10, 'improvement')
    
    # Flatten the multi-level column index
    top_improvers_flat = top_improvers.reset_index()
    top_improvers_flat.columns = ['_'.join(col).strip() for col in top_improvers_flat.columns.values]


    fig_improvement = px.bar(top_improvers_flat, x='player_', y='improvement_', 
                             title="Top 10 Players by Expected Velo Improvement (%)")
    st.plotly_chart(fig_improvement)

    # Correlation between metrics
    st.subheader("Metric Correlations")
    correlation_matrix = gym_filtered_df[metrics].corr()
    fig_corr = px.imshow(correlation_matrix, title="Correlation between Metrics")
    st.plotly_chart(fig_corr)

# Main app
def main():
    st.set_page_config(page_title="Academy Metrics Dashboard", layout="wide")

    # Add additional images to the sidebar
    st.sidebar.image("images/logo.png")
    
    st.sidebar.title("Navigation")
    
    # Main content area title
    st.title("Academy Metrics Dashboard")
    
    # Generate mock data
    df = generate_mock_data()
    
    # Ensure 'date' column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Display the academy page
    academy_page(df)

if __name__ == "__main__":
    main()