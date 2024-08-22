import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, date, timedelta

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
                'throwing_velo': np.random.normal(85, 5),
                'actively_hurt': np.random.choice([True, False], p=[0.05, 0.95]),
                'total_injuries': np.random.randint(0, 3),
                'location': np.random.choice(['In-gym', 'Remote']),
                'level': np.random.choice(['Youth', 'High School', 'College', 'Professional']),
                'workout_type': np.random.choice(['mocap', 'pen', 'hybrid A', 'hybrid B', 'recovery', 'Live At-Bats', 'In-Game Collection'])
            })
    
    df = pd.DataFrame(data)
    df['total'] = len(players)  # Total number of players
    return df

# Calculate changes in metrics for a specific time period
def calculate_changes(df, start_date, end_date, location, level):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    
    df_filtered = df[(df['date'] >= start_datetime) & (df['date'] <= end_datetime) & 
                     (df['location'] == location) & (df['level'] == level)]
    
    metrics = ['max_throwing_velo', 'bat_speed', 'top_8th_ev', 'expected_velo', 'throwing_velo']
    
    start_values = df_filtered[df_filtered['date'] == df_filtered['date'].min()].groupby('player')[metrics].mean()
    end_values = df_filtered[df_filtered['date'] == df_filtered['date'].max()].groupby('player')[metrics].mean()
    
    changes = ((end_values - start_values) / start_values * 100).fillna(0)
    
    # Calculate injury rate change
    start_injuries = df_filtered[df_filtered['date'] == df_filtered['date'].min()]['actively_hurt'].mean() * 100
    end_injuries = df_filtered[df_filtered['date'] == df_filtered['date'].max()]['actively_hurt'].mean() * 100
    injury_rate_change = end_injuries - start_injuries
    
    changes['injury_rate'] = injury_rate_change
    
    return changes

# Calculate KPIs
def calculate_kpis(df, start_date, end_date, location, level):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    
    df_filtered = df[(df['date'] >= start_datetime) & (df['date'] <= end_datetime) & 
                     (df['location'] == location) & (df['level'] == level)]
    
    high_intensity_workouts = ['mocap', 'pen', 'hybrid A']
    
    kpis = {
        "Pitching": {
            "Max Velo (High Intensity)": df_filtered[df_filtered['workout_type'].isin(high_intensity_workouts)]['max_throwing_velo'].max()
        },
        "Hitting": {
            "Bat Speed": df_filtered['bat_speed'].mean(),
            "Top 8th EV": df_filtered['top_8th_ev'].mean()
        },
        "HP": {
            "Expected Velo": df_filtered['expected_velo'].mean()
        },
        "Academy": {
            "Expected Velo": df_filtered['expected_velo'].mean(),
            "Throwing Velo": df_filtered['throwing_velo'].mean(),
            "Bat Speed": df_filtered['bat_speed'].mean()
        },
        "Injury Tracker": {
            "Active DL": df_filtered['actively_hurt'].mean() * 100,
            "Total Injuries": df_filtered['total_injuries'].sum(),
            "Total Players": df_filtered['total'].iloc[0]
        }
    }
    
    return kpis

# Display changes for a specific time period
def display_changes(changes, title):
    st.subheader(title)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top Improved Variables")
        top_improved = changes.mean().nlargest(3).reset_index()
        top_improved.columns = ['Metric', 'Change']
        st.dataframe(top_improved, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Most Depreciated Variables")
        most_depreciated = changes.mean().nsmallest(3).reset_index()
        most_depreciated.columns = ['Metric', 'Change']
        st.dataframe(most_depreciated, hide_index=True, use_container_width=True)

    with col3:
        st.subheader("Most Static Variables")
        most_static = changes.mean().abs().nsmallest(3).reset_index()
        most_static.columns = ['Metric', 'Change']
        st.dataframe(most_static, hide_index=True, use_container_width=True)

# Main dashboard
def main_dashboard(df):
    st.title("Athlete KPI Summary Dashboard")

    # Sidebar
    st.sidebar.title("Filters")
    location = st.sidebar.selectbox("Location", ["In-gym", "Remote"])
    level = st.sidebar.selectbox("Level", ["Youth", "High School", "College", "Professional"])

    # Calculate end date (today) and start dates for different periods
    end_date = df['date'].max().date()
    start_date_30d = end_date - timedelta(days=30)
    start_date_90d = end_date - timedelta(days=90)
    start_date_prev_period = end_date - timedelta(days=60)
    start_date_prev_year = end_date - timedelta(days=365)

    # Calculate changes for different time periods
    changes_30d = calculate_changes(df, start_date_30d, end_date, location, level)
    changes_90d = calculate_changes(df, start_date_90d, end_date, location, level)
    changes_prev_period = calculate_changes(df, start_date_prev_period, end_date, location, level)
    changes_prev_year = calculate_changes(df, start_date_prev_year, end_date, location, level)

    # Display changes for all time periods
    display_changes(changes_30d, "Last 30 Days")
    display_changes(changes_90d, "Last 90 Days")
    display_changes(changes_prev_period, "vs. Previous Period (60 days)")
    display_changes(changes_prev_year, "vs. Previous Year")

    # Calculate and display KPIs (using the 30-day period as default)
    kpis = calculate_kpis(df, start_date_30d, end_date, location, level)

    # Display KPIs in expandable sections
    for category, metrics in kpis.items():
        with st.expander(f"{category} KPIs"):
            cols = st.columns(len(metrics))
            for i, (metric_name, value) in enumerate(metrics.items()):
                with cols[i]:
                    st.metric(metric_name, f"{value:.2f}")

    # Injury Tracker Charts
    with st.expander("Injury Tracker Charts"):
        injury_data = kpis["Injury Tracker"]
        
        fig = px.pie(values=[injury_data["Active DL"], 100 - injury_data["Active DL"]], 
                names=["Active DL", "Healthy"], 
                title="Active DL vs Healthy Players")
        st.plotly_chart(fig)

        fig = px.bar(x=["Total Injuries", "Total Players"], 
                y=[injury_data["Total Injuries"], injury_data["Total Players"]],
                labels={"x": "Category", "y": "Count"},
                title="Total Injuries vs Total Players")
        st.plotly_chart(fig)

# Main app
def main():
    st.set_page_config(page_title="Athlete KPI Dashboard", layout="wide")
    # Add additional images to the sidebar
    st.sidebar.image("images/logo.png")
    # Generate mock data
    df = generate_mock_data()
    
    # Ensure 'date' column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Display the main dashboard
    main_dashboard(df)

if __name__ == "__main__":
    main()
