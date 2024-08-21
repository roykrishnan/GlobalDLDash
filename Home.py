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
                'workout_type': np.random.choice(['mocap', 'pen', 'hybrid A', 'hybrid B', 'recovery', 'Live At-Bats', 'In-Game Collection'])
            })
    
    df = pd.DataFrame(data)
    df['total'] = len(players)  # Total number of players
    return df

# Time period selection
def select_time_period(df):
    end_date = df['date'].max().date()
    
    col1, col2, col3, col4 = st.columns(4)
    
    if col1.button("Last 30 days", key="btn_30_days"):
        return end_date - timedelta(days=30), end_date, "Last 30 days"
    if col2.button("Last 90 days", key="btn_90_days"):
        return end_date - timedelta(days=90), end_date, "Last 90 days"
    if col3.button("vs. Previous Period", key="btn_prev_period"):
        return end_date - timedelta(days=60), end_date, "vs. Previous Period"
    if col4.button("vs. Previous Year", key="btn_prev_year"):
        return end_date - timedelta(days=365), end_date, "vs. Previous Year"
    
    # Return current values if no button is clicked
    return st.session_state.start_date, st.session_state.end_date, st.session_state.selected_period

# Calculate changes in metrics
def calculate_changes(df, start_date, end_date, location):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    df_filtered = df[(df['date'] >= start_datetime) & (df['date'] <= end_datetime) & (df['location'] == location)]
    
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
def calculate_kpis(df, start_date, end_date, location):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    df_filtered = df[(df['date'] >= start_datetime) & (df['date'] <= end_datetime) & (df['location'] == location)]
    
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

# Main dashboard
def main_dashboard(df):
    st.title("Athlete KPI Summary Dashboard")

    # Sidebar
    st.sidebar.title("Filters")
    location = st.sidebar.selectbox("Location", ["In-gym", "Remote"])

    # Initialize session state for date range if not exists
    if 'start_date' not in st.session_state:
        st.session_state.start_date = df['date'].max().date() - timedelta(days=30)
    if 'end_date' not in st.session_state:
        st.session_state.end_date = df['date'].max().date()
    if 'selected_period' not in st.session_state:
        st.session_state.selected_period = "Last 30 days"

    # Time period selection
    new_start_date, new_end_date, new_selected_period = select_time_period(df)
    
    # Update session state if a new period is selected
    if new_selected_period != st.session_state.selected_period:
        st.session_state.start_date = new_start_date
        st.session_state.end_date = new_end_date
        st.session_state.selected_period = new_selected_period

    st.write(f"Selected period: {st.session_state.selected_period}")

    # Calculate changes and KPIs based on the selected period
    changes = calculate_changes(df, st.session_state.start_date, st.session_state.end_date, location)
    kpis = calculate_kpis(df, st.session_state.start_date, st.session_state.end_date, location)

    # Display top improved, depreciated, and static variables
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
