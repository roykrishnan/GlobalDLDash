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
                'max_throwing_velo': np.random.normal(85, 5),
                'bat_speed': np.random.normal(70, 5),
                'top_8th_ev': np.random.normal(95, 3),
                'expected_velo': np.random.normal(92, 3),
                'rate_of_force_production': np.random.normal(1000, 100),
                'best_rotational_force_increase': np.random.normal(50, 10),
                'best_linear_force_increase': np.random.normal(40, 8),
                'best_total_force_increase': np.random.normal(90, 15),
                'throwing_velo': np.random.normal(85, 5),
                'actively_hurt': np.random.choice([True, False], p=[0.05, 0.95]),
                'total_injuries': np.random.randint(0, 3),
                'gym': np.random.choice(['WA', 'AZ', 'FL', 'Remote']),
                'workout_type': np.random.choice(['mocap', 'pen', 'hybrid A', 'hybrid B', 'recovery', 'Live At-Bats', 'In-Game Collection'])
            })
    
    df = pd.DataFrame(data)
    df['total'] = len(players)  # Total number of players
    return df

# Time period selection
def select_time_period(df):
    col1, col2, col3, col4 = st.columns(4)
    
    end_date = df['date'].max().date()
    
    with col1:
        last_30 = st.button("Last 30 days")
    with col2:
        last_90 = st.button("Last 90 days")
    with col3:
        vs_previous = st.button("vs. Previous Period")
    with col4:
        vs_year = st.button("vs. Previous Year")
    
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

# Calculate changes in metrics
def calculate_changes(df, start_date, end_date):
    metrics = ['max_throwing_velo', 'bat_speed', 'top_8th_ev', 'expected_velo', 'rate_of_force_production',
               'best_rotational_force_increase', 'best_linear_force_increase', 'best_total_force_increase',
               'throwing_velo']
    
    start_values = df[df['date'].dt.date == start_date].groupby('player')[metrics].mean()
    end_values = df[df['date'].dt.date == end_date].groupby('player')[metrics].mean()
    
    changes = ((end_values - start_values) / start_values * 100).fillna(0)
    
    # Calculate injury rate change
    start_injuries = df[df['date'].dt.date == start_date]['actively_hurt'].mean() * 100
    end_injuries = df[df['date'].dt.date == end_date]['actively_hurt'].mean() * 100
    injury_rate_change = end_injuries - start_injuries
    
    changes['injury_rate'] = injury_rate_change
    
    return changes

# Function to generate biggest movers table
def generate_biggest_movers(df, start_date, end_date):
    changes = calculate_changes(df, start_date, end_date)
    
    top_gainers = changes.mean().nlargest(5)
    top_losers = changes.mean().nsmallest(5)
    most_static = changes.mean().abs().nsmallest(5)
    
    movers_data = pd.concat([
        top_gainers.to_frame('Top Gainers'),
        top_losers.to_frame('Top Losers'),
        most_static.to_frame('Most Static')
    ], axis=1)
    
    return movers_data.fillna(0)

# Main dashboard
def main_dashboard(df):
    st.title("Athlete KPI Dashboard")

    # Expander with explanations
    with st.expander("Dashboard Explanation"):
        st.write("""
        This dashboard provides an overview of athlete performance metrics:
        - **Top Improved Variables**: Metrics that have shown the most positive change.
        - **Most Depreciated Variables**: Metrics that have declined the most.
        - **Most Static Variables**: Metrics that have changed the least.
        - **Biggest Movers**: A detailed view of the metrics with the most significant changes.
        
        The pages to the right provide deeper dives by department to view recent improvements/limitations. 
        """)

    # Time period selection
    start_date, end_date, selected_period = select_time_period(df)

    # Calculate changes
    all_changes = calculate_changes(df, start_date, end_date)

    # Display top improved, depreciated, and static variables
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top Improved Variables")
        st.table(all_changes.mean().nlargest(3).round(2))

    with col2:
        st.subheader("Most Depreciated Variables")
        st.table(all_changes.mean().nsmallest(3).round(2))

    with col3:
        st.subheader("Most Static Variables")
        st.table(all_changes.mean().abs().nsmallest(3).round(2))

    # Generate and display biggest movers table
    st.subheader("Biggest Movers")
    biggest_movers = generate_biggest_movers(df, start_date, end_date)
    
    # Convert the biggest_movers DataFrame to long format for easier plotting
    biggest_movers_long = biggest_movers.reset_index().melt(id_vars='index', var_name='Category', value_name='Change')
    biggest_movers_long = biggest_movers_long.rename(columns={'index': 'Metric'})

    # Create a grouped bar chart
    fig = px.bar(biggest_movers_long, x='Metric', y='Change', color='Category', barmode='group',
                 title="Biggest Movers by Category",
                 labels={'Metric': 'Performance Metric', 'Change': 'Percentage Change'},
                 height=500)
    st.plotly_chart(fig)

    # Display the table
    st.table(biggest_movers.round(2))

# Main app
def main():
    st.set_page_config(page_title="Athlete KPI Dashboard", layout="wide")

    # Add logo to the sidebar
    st.sidebar.image("images/logo.png")
    
    # Generate mock data
    df = generate_mock_data()
    
    # Ensure 'date' column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Display the main dashboard
    main_dashboard(df)

if __name__ == "__main__":
    main()