"""
EV Analytics Dashboard - Streamlit App
======================================
A comprehensive electric vehicle analytics platform with three scenarios:
1. Charging Pattern & Usage Analysis (City Energy Planners)
2. Battery Performance vs Driving Range (Fleet Managers)
3. Comparative EV Model Efficiency Dashboard (Consumers)

Integrated with Gemini AI for intelligent insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta
import google.generativeai as genai
import os


# Preferred models ordered by cost/speed balance and broad availability.
PREFERRED_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# Page configuration
st.set_page_config(
    page_title="EV Analytics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scenario-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini AI
def _resolve_gemini_model_name():
    """Choose a Gemini model that supports generateContent."""
    try:
        available = []
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            if "generateContent" in methods:
                available.append(model.name.replace("models/", ""))

        for preferred in PREFERRED_GEMINI_MODELS:
            if preferred in available:
                return preferred

        if available:
            # Use any available model as a fallback if preferred ones are absent.
            return available[0]
    except Exception:
        # If listing models fails (network/permissions), use the safest default.
        pass

    return PREFERRED_GEMINI_MODELS[0]


@st.cache_resource
def init_gemini():
    """Initialize Gemini AI model"""
    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(_resolve_gemini_model_name())
            return model
        return None
    except Exception as e:
        st.warning(f"Gemini AI not configured: {e}")
        return None

gemini_model = init_gemini()

def get_ai_insights(prompt):
    """Get AI insights from Gemini"""
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Insights temporarily unavailable. Error: {str(e)}"
    return "💡 Configure GEMINI_API_KEY environment variable to enable AI insights."

# ==================== DATA GENERATION FUNCTIONS ====================

@st.cache_data
def generate_charging_data():
    """Generate sample charging pattern data for Scenario 1"""
    np.random.seed(42)
    
    # Generate 5000 charging sessions
    n_sessions = 5000
    
    # Time of day distribution (peak hours: 6-9 AM, 6-10 PM)
    hours = []
    for _ in range(n_sessions):
        if np.random.random() < 0.4:  # 40% peak hours
            hour = np.random.choice([6, 7, 8, 18, 19, 20, 21, 22])
        else:
            hour = np.random.randint(0, 24)
        hours.append(hour)
    
    # Neighborhoods
    neighborhoods = ['Downtown', 'Suburb North', 'Suburb South', 'Industrial', 'University', 'Airport', 'Mall District']
    neighborhood_weights = [0.25, 0.20, 0.18, 0.12, 0.10, 0.08, 0.07]
    
    # Charging station types
    station_types = ['Level 1 (Slow)', 'Level 2 (Standard)', 'DC Fast Charging']
    station_weights = [0.15, 0.55, 0.30]
    
    data = {
        'session_id': range(1, n_sessions + 1),
        'timestamp': [datetime(2024, 1, 1) + timedelta(days=int(np.random.randint(0, 365)), hours=int(h)) for h in hours],
        'hour_of_day': hours,
        'neighborhood': np.random.choice(neighborhoods, n_sessions, p=neighborhood_weights),
        'station_type': np.random.choice(station_types, n_sessions, p=station_weights),
        'duration_minutes': np.random.gamma(2, 30) + np.random.randint(15, 180, n_sessions),
        'power_kwh': np.random.gamma(3, 8, n_sessions),
        'vehicle_type': np.random.choice(['Sedan', 'SUV', 'Truck', 'Compact'], n_sessions, p=[0.35, 0.30, 0.15, 0.20]),
        'user_type': np.random.choice(['Residential', 'Commercial', 'Fleet'], n_sessions, p=[0.60, 0.25, 0.15]),
    }
    
    df = pd.DataFrame(data)
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['month'] = df['timestamp'].dt.month_name()
    
    # Calculate cost based on station type
    cost_per_kwh = {'Level 1 (Slow)': 0.12, 'Level 2 (Standard)': 0.18, 'DC Fast Charging': 0.35}
    df['cost_usd'] = df.apply(lambda x: x['power_kwh'] * cost_per_kwh[x['station_type']], axis=1)
    
    return df

@st.cache_data
def generate_battery_data():
    """Generate battery performance data for Scenario 2"""
    np.random.seed(123)
    
    n_vehicles = 150
    n_records = 10000
    
    vehicle_ids = [f"EV-{str(i).zfill(4)}" for i in range(1, n_vehicles + 1)]
    
    data = []
    for _ in range(n_records):
        vehicle_id = np.random.choice(vehicle_ids)
        vehicle_age = np.random.randint(0, 5)  # 0-4 years
        total_cycles = np.random.randint(50, 1500)
        
        # Battery health degrades with age and cycles
        base_health = 100 - (vehicle_age * 3) - (total_cycles * 0.02)
        battery_health = max(60, min(100, base_health + np.random.normal(0, 3)))
        
        # State of charge
        soc = np.random.uniform(10, 100)
        
        # Depth of discharge
        dod = np.random.uniform(20, 80)
        
        # Temperature effect
        temp = np.random.normal(25, 10)
        temp_factor = 1 - abs(temp - 25) * 0.01
        
        # Driving conditions
        condition = np.random.choice(['City', 'Highway', 'Mixed', 'Hilly'], p=[0.35, 0.30, 0.25, 0.10])
        condition_factors = {'City': 0.85, 'Highway': 1.0, 'Mixed': 0.90, 'Hilly': 0.75}
        
        # Calculate actual range
        base_range = 400  # km
        predicted_range = base_range * (battery_health / 100) * condition_factors[condition]
        actual_range = predicted_range * temp_factor * np.random.uniform(0.85, 1.05)
        
        # Efficiency
        efficiency = (actual_range / (100 - soc) * 100) / 4  # km/kWh approximation
        
        data.append({
            'vehicle_id': vehicle_id,
            'timestamp': datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365)),
            'vehicle_age_years': vehicle_age,
            'charging_cycles': total_cycles,
            'battery_health_percent': round(battery_health, 1),
            'state_of_charge_percent': round(soc, 1),
            'depth_of_discharge_percent': round(dod, 1),
            'temperature_celsius': round(temp, 1),
            'driving_condition': condition,
            'predicted_range_km': round(predicted_range, 1),
            'actual_range_km': round(actual_range, 1),
            'efficiency_km_kwh': round(efficiency, 2),
            'needs_replacement': battery_health < 70
        })
    
    return pd.DataFrame(data)

@st.cache_data
def generate_ev_models_data():
    """Generate EV model comparison data for Scenario 3"""
    
    ev_models = [
        {'model': 'Tesla Model 3', 'brand': 'Tesla', 'price_usd': 38990, 'range_km': 438, 'battery_kwh': 57.5, 'charging_time_h': 0.5, 'co2_g_km': 0, 'category': 'Sedan'},
        {'model': 'Tesla Model Y', 'brand': 'Tesla', 'price_usd': 47740, 'range_km': 455, 'battery_kwh': 75, 'charging_time_h': 0.6, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'Nissan Leaf', 'brand': 'Nissan', 'price_usd': 28400, 'range_km': 270, 'battery_kwh': 40, 'charging_time_h': 0.7, 'co2_g_km': 0, 'category': 'Compact'},
        {'model': 'Chevy Bolt EV', 'brand': 'Chevrolet', 'price_usd': 26500, 'range_km': 416, 'battery_kwh': 65, 'charging_time_h': 0.9, 'co2_g_km': 0, 'category': 'Compact'},
        {'model': 'Ford Mustang Mach-E', 'brand': 'Ford', 'price_usd': 42995, 'range_km': 440, 'battery_kwh': 70, 'charging_time_h': 0.6, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'Hyundai Ioniq 5', 'brand': 'Hyundai', 'price_usd': 41450, 'range_km': 488, 'battery_kwh': 77.4, 'charging_time_h': 0.3, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'Kia EV6', 'brand': 'Kia', 'price_usd': 42900, 'range_km': 499, 'battery_kwh': 77.4, 'charging_time_h': 0.3, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'BMW i4', 'brand': 'BMW', 'price_usd': 51400, 'range_km': 475, 'battery_kwh': 83.9, 'charging_time_h': 0.5, 'co2_g_km': 0, 'category': 'Sedan'},
        {'model': 'VW ID.4', 'brand': 'Volkswagen', 'price_usd': 38995, 'range_km': 418, 'battery_kwh': 77, 'charging_time_h': 0.6, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'Audi e-tron', 'brand': 'Audi', 'price_usd': 65900, 'range_km': 441, 'battery_kwh': 95, 'charging_time_h': 0.5, 'co2_g_km': 0, 'category': 'SUV'},
        {'model': 'Polestar 2', 'brand': 'Polestar', 'price_usd': 48900, 'range_km': 440, 'battery_kwh': 78, 'charging_time_h': 0.5, 'co2_g_km': 0, 'category': 'Sedan'},
        {'model': 'Rivian R1T', 'brand': 'Rivian', 'price_usd': 73900, 'range_km': 505, 'battery_kwh': 135, 'charging_time_h': 0.7, 'co2_g_km': 0, 'category': 'Truck'},
        {'model': 'Lucid Air', 'brand': 'Lucid', 'price_usd': 77400, 'range_km': 832, 'battery_kwh': 118, 'charging_time_h': 0.4, 'co2_g_km': 0, 'category': 'Sedan'},
        {'model': 'BYD Dolphin', 'brand': 'BYD', 'price_usd': 28000, 'range_km': 340, 'battery_kwh': 44.9, 'charging_time_h': 0.8, 'co2_g_km': 0, 'category': 'Compact'},
        {'model': 'MG ZS EV', 'brand': 'MG', 'price_usd': 26000, 'range_km': 320, 'battery_kwh': 50.3, 'charging_time_h': 0.9, 'co2_g_km': 0, 'category': 'SUV'},
    ]
    
    df = pd.DataFrame(ev_models)
    
    # Calculate efficiency metrics
    df['efficiency_km_kwh'] = (df['range_km'] / df['battery_kwh']).round(2)
    df['cost_per_km'] = (df['price_usd'] / df['range_km']).round(2)
    
    # Calculate charging cost (assuming $0.20 per kWh average)
    electricity_rate = 0.20
    df['charging_cost_usd'] = (df['battery_kwh'] * electricity_rate).round(2)
    df['cost_per_100km'] = ((df['battery_kwh'] / df['range_km']) * 100 * electricity_rate).round(2)
    
    # Compare with ICE vehicle (assuming 8L/100km, $1.50/L)
    ice_cost_per_100km = 8 * 1.50
    df['savings_per_100km_vs_ice'] = (ice_cost_per_100km - df['cost_per_100km']).round(2)
    df['annual_savings_vs_ice'] = (df['savings_per_100km_vs_ice'] * 150).round(0)  # 15,000 km/year
    
    # CO2 savings (assuming ICE emits 120g/km)
    ice_co2_per_year = 120 * 15000 / 1000  # kg
    df['annual_co2_savings_kg'] = ice_co2_per_year
    
    # 5-year total cost of ownership
    df['5year_tco'] = (df['price_usd'] + (df['cost_per_100km'] * 150 * 5)).round(0)
    
    return df

# ==================== SCENARIO 1: CHARGING PATTERN ANALYSIS ====================

def scenario_charging_analysis():
    """Charging Pattern and Usage Analysis Dashboard"""
    
    st.markdown("## 🔌 Scenario 1: Charging Pattern & Usage Analysis")
    st.markdown("*For City Energy Planners like Aarav*")
    
    df = generate_charging_data()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_neighborhoods = st.multiselect(
            "Select Neighborhoods",
            options=df['neighborhood'].unique(),
            default=df['neighborhood'].unique()[:3]
        )
    with col2:
        selected_station_types = st.multiselect(
            "Station Types",
            options=df['station_type'].unique(),
            default=df['station_type'].unique()
        )
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=[df['timestamp'].min().date(), df['timestamp'].max().date()],
            min_value=df['timestamp'].min().date(),
            max_value=df['timestamp'].max().date()
        )
    
    # Filter data
    filtered_df = df[
        (df['neighborhood'].isin(selected_neighborhoods)) &
        (df['station_type'].isin(selected_station_types)) &
        (df['timestamp'].dt.date >= date_range[0]) &
        (df['timestamp'].dt.date <= date_range[1])
    ]
    
    # Key Metrics
    st.markdown("### 📊 Key Metrics")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total Sessions", f"{len(filtered_df):,}")
    with m2:
        st.metric("Total Energy (MWh)", f"{filtered_df['power_kwh'].sum() / 1000:.1f}")
    with m3:
        st.metric("Avg Session Duration", f"{filtered_df['duration_minutes'].mean():.0f} min")
    with m4:
        st.metric("Peak Hour Demand", f"{filtered_df[filtered_df['hour_of_day'].isin([18,19,20,21])]['power_kwh'].sum() / 1000:.1f} MWh")
    
    # Visualizations
    st.markdown("### 📈 Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["⏰ Peak Hours Analysis", "🗺️ Geographic Heatmap", "📅 Usage Trends", "💰 Cost Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Hourly charging pattern
            hourly_data = filtered_df.groupby('hour_of_day').agg({
                'power_kwh': 'sum',
                'session_id': 'count'
            }).reset_index()
            hourly_data.columns = ['Hour', 'Total Energy (kWh)', 'Number of Sessions']
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=hourly_data['Hour'],
                y=hourly_data['Total Energy (kWh)'],
                name='Energy Consumed',
                marker_color='#3B82F6'
            ))
            fig.add_trace(go.Scatter(
                x=hourly_data['Hour'],
                y=hourly_data['Number of Sessions'],
                name='Sessions',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#EF4444', width=3)
            ))
            
            fig.update_layout(
                title='Charging Patterns by Hour of Day',
                xaxis_title='Hour of Day',
                yaxis_title='Energy (kWh)',
                yaxis2=dict(title='Number of Sessions', overlaying='y', side='right'),
                legend=dict(x=0.01, y=0.99),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Peak vs Off-peak comparison
            peak_hours = [6, 7, 8, 18, 19, 20, 21, 22]
            filtered_df['period'] = filtered_df['hour_of_day'].apply(
                lambda x: 'Peak Hours' if x in peak_hours else 'Off-Peak Hours'
            )
            
            period_data = filtered_df.groupby('period').agg({
                'power_kwh': ['sum', 'mean'],
                'session_id': 'count'
            }).reset_index()
            period_data.columns = ['Period', 'Total Energy', 'Avg Energy/Session', 'Sessions']
            
            fig = px.pie(period_data, values='Total Energy', names='Period',
                        title='Peak vs Off-Peak Energy Distribution',
                        color_discrete_sequence=['#F59E0B', '#10B981'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Neighborhood heatmap
        neighborhood_data = filtered_df.groupby('neighborhood').agg({
            'power_kwh': 'sum',
            'session_id': 'count',
            'cost_usd': 'sum'
        }).reset_index()
        
        fig = px.treemap(neighborhood_data, 
                        path=['neighborhood'],
                        values='power_kwh',
                        color='session_id',
                        color_continuous_scale='Viridis',
                        title='Energy Consumption by Neighborhood (Treemap)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap by hour and neighborhood
        heatmap_data = filtered_df.groupby(['neighborhood', 'hour_of_day'])['power_kwh'].sum().unstack(fill_value=0)
        
        fig = px.imshow(heatmap_data,
                       labels=dict(x="Hour of Day", y="Neighborhood", color="Energy (kWh)"),
                       title="Charging Heatmap: Neighborhood vs Hour",
                       color_continuous_scale="YlOrRd")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly trends
            monthly_data = filtered_df.groupby('month').agg({
                'power_kwh': 'sum',
                'session_id': 'count'
            }).reindex(['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'])
            monthly_data = monthly_data.reset_index()
            monthly_data = monthly_data.dropna()
            
            fig = px.line(monthly_data, x='month', y='power_kwh',
                         title='Monthly Energy Consumption Trend',
                         markers=True)
            fig.update_xaxes(title='Month')
            fig.update_yaxes(title='Energy (kWh)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Day of week analysis
            dow_data = filtered_df.groupby('day_of_week').agg({
                'power_kwh': 'sum',
                'session_id': 'count'
            }).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            dow_data = dow_data.reset_index()
            
            fig = px.bar(dow_data, x='day_of_week', y='power_kwh',
                        title='Energy Consumption by Day of Week',
                        color='power_kwh',
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by station type
            revenue_data = filtered_df.groupby('station_type')['cost_usd'].sum().reset_index()
            
            fig = px.bar(revenue_data, x='station_type', y='cost_usd',
                        title='Revenue by Station Type',
                        color='station_type')
            fig.update_xaxes(title='Station Type')
            fig.update_yaxes(title='Revenue ($)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cost per user type
            user_cost = filtered_df.groupby('user_type').agg({
                'cost_usd': ['sum', 'mean'],
                'session_id': 'count'
            }).reset_index()
            user_cost.columns = ['User Type', 'Total Revenue', 'Avg Cost/Session', 'Sessions']
            
            fig = px.scatter(user_cost, x='Sessions', y='Total Revenue',
                            size='Avg Cost/Session', color='User Type',
                            title='Revenue vs Sessions by User Type')
            st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights
    st.markdown("### 🤖 AI-Powered Insights")
    
    if st.button("Generate Insights for Aarav"):
        with st.spinner("Analyzing data with Gemini AI..."):
            peak_hour_pct = (filtered_df[filtered_df['hour_of_day'].isin([18,19,20,21])]['power_kwh'].sum() / 
                           filtered_df['power_kwh'].sum() * 100)
            
            prompt = f"""As a city energy planner, analyze this EV charging data:
            - Total charging sessions: {len(filtered_df):,}
            - Total energy consumed: {filtered_df['power_kwh'].sum()/1000:.1f} MWh
            - Peak hours (6-9 PM) account for {peak_hour_pct:.1f}% of total demand
            - Top neighborhood by demand: {filtered_df.groupby('neighborhood')['power_kwh'].sum().idxmax()}
            - Most popular station type: {filtered_df['station_type'].mode().values[0]}
            
            Provide 3-4 actionable insights for grid stability and infrastructure planning.
            Focus on peak demand management and equitable infrastructure distribution."""
            
            insights = get_ai_insights(prompt)
            st.info(insights)

# ==================== SCENARIO 2: BATTERY PERFORMANCE ====================

def scenario_battery_performance():
    """Battery Performance vs Driving Range Dashboard"""
    
    st.markdown("## 🔋 Scenario 2: Battery Performance vs Driving Range")
    st.markdown("*For Fleet Managers like Meera*")
    
    df = generate_battery_data()
    
    # Fleet Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fleet Size", f"{df['vehicle_id'].nunique()}")
    with col2:
        avg_health = df.groupby('vehicle_id')['battery_health_percent'].last().mean()
        st.metric("Avg Battery Health", f"{avg_health:.1f}%")
    with col3:
        vehicles_needing_replacement = df.groupby('vehicle_id')['battery_health_percent'].last()
        st.metric("Needs Replacement", f"{(vehicles_needing_replacement < 70).sum()}")
    with col4:
        avg_efficiency = df['efficiency_km_kwh'].mean()
        st.metric("Fleet Avg Efficiency", f"{avg_efficiency:.1f} km/kWh")
    
    # Filters
    st.markdown("### 🔍 Fleet Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_vehicles = st.multiselect(
            "Select Vehicles",
            options=sorted(df['vehicle_id'].unique()),
            default=sorted(df['vehicle_id'].unique())[:10]
        )
    with col2:
        health_range = st.slider(
            "Battery Health Range (%)",
            min_value=50, max_value=100,
            value=(60, 100)
        )
    with col3:
        driving_conditions = st.multiselect(
            "Driving Conditions",
            options=df['driving_condition'].unique(),
            default=df['driving_condition'].unique()
        )
    
    # Filter data
    filtered_df = df[
        (df['vehicle_id'].isin(selected_vehicles)) &
        (df['battery_health_percent'] >= health_range[0]) &
        (df['battery_health_percent'] <= health_range[1]) &
        (df['driving_condition'].isin(driving_conditions))
    ]
    
    # Visualizations
    st.markdown("### 📈 Performance Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔋 Battery Health", "📊 Range Analysis", "🌡️ Temperature Impact", "⚠️ Maintenance Alerts"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Battery health distribution
            fig = px.histogram(filtered_df, x='battery_health_percent',
                             nbins=30,
                             title='Battery Health Distribution',
                             color_discrete_sequence=['#10B981'])
            fig.add_vline(x=70, line_dash="dash", line_color="red",
                         annotation_text="Replacement Threshold")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Battery health vs charging cycles
            cycle_health = filtered_df.groupby('vehicle_id').agg({
                'charging_cycles': 'max',
                'battery_health_percent': 'last'
            }).reset_index()
            
            fig = px.scatter(cycle_health, x='charging_cycles', y='battery_health_percent',
                           title='Battery Health vs Charging Cycles',
                           trendline='ols',
                           color='battery_health_percent',
                           color_continuous_scale='RdYlGn')
            fig.add_hline(y=70, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Predicted vs Actual Range
            fig = px.scatter(filtered_df, x='predicted_range_km', y='actual_range_km',
                           color='battery_health_percent',
                           color_continuous_scale='Viridis',
                           title='Predicted vs Actual Range',
                           opacity=0.6)
            
            # Add perfect prediction line
            max_range = max(filtered_df['predicted_range_km'].max(), filtered_df['actual_range_km'].max())
            fig.add_trace(go.Scatter(x=[0, max_range], y=[0, max_range],
                                    mode='lines', name='Perfect Prediction',
                                    line=dict(color='red', dash='dash')))
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Range by driving condition
            range_by_condition = filtered_df.groupby('driving_condition').agg({
                'actual_range_km': 'mean',
                'predicted_range_km': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Actual Range', x=range_by_condition['driving_condition'],
                               y=range_by_condition['actual_range_km'], marker_color='#3B82F6'))
            fig.add_trace(go.Bar(name='Predicted Range', x=range_by_condition['driving_condition'],
                               y=range_by_condition['predicted_range_km'], marker_color='#9CA3AF'))
            
            fig.update_layout(title='Range by Driving Condition',
                            barmode='group',
                            yaxis_title='Range (km)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature vs Efficiency
            temp_bins = pd.cut(filtered_df['temperature_celsius'], bins=10)
            temp_efficiency = filtered_df.groupby(temp_bins)['efficiency_km_kwh'].mean().reset_index()
            temp_efficiency['temperature_celsius'] = temp_efficiency['temperature_celsius'].apply(lambda x: x.mid)
            
            fig = px.line(temp_efficiency, x='temperature_celsius', y='efficiency_km_kwh',
                         title='Efficiency vs Temperature',
                         markers=True)
            fig.update_xaxes(title='Temperature (°C)')
            fig.update_yaxes(title='Efficiency (km/kWh)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Temperature vs Range deviation
            filtered_df['range_deviation'] = ((filtered_df['actual_range_km'] - filtered_df['predicted_range_km']) 
                                             / filtered_df['predicted_range_km'] * 100)
            
            fig = px.scatter(filtered_df, x='temperature_celsius', y='range_deviation',
                           color='battery_health_percent',
                           title='Range Deviation vs Temperature',
                           opacity=0.5)
            fig.add_hline(y=0, line_dash="dash", line_color="green")
            fig.update_yaxes(title='Range Deviation (%)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Maintenance alerts
        latest_data = df.groupby('vehicle_id').agg({
            'battery_health_percent': 'last',
            'charging_cycles': 'max',
            'vehicle_age_years': 'last',
            'needs_replacement': 'last'
        }).reset_index()
        
        alerts = latest_data[latest_data['needs_replacement'] == True]
        warnings = latest_data[(latest_data['battery_health_percent'] >= 70) & 
                              (latest_data['battery_health_percent'] < 80)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚨 Critical Alerts (Replacement Needed)")
            if len(alerts) > 0:
                st.dataframe(alerts[['vehicle_id', 'battery_health_percent', 'charging_cycles', 'vehicle_age_years']],
                           use_container_width=True)
            else:
                st.success("No vehicles require immediate battery replacement!")
        
        with col2:
            st.markdown("#### ⚠️ Warnings (Health 70-80%)")
            if len(warnings) > 0:
                st.dataframe(warnings[['vehicle_id', 'battery_health_percent', 'charging_cycles', 'vehicle_age_years']],
                           use_container_width=True)
            else:
                st.success("No warning-level vehicles!")
        
        # Battery degradation forecast
        st.markdown("#### 📉 Battery Degradation Forecast")
        
        # Simulate future degradation
        forecast_data = []
        for vehicle in selected_vehicles[:5]:  # Show first 5 selected vehicles
            vehicle_data = latest_data[latest_data['vehicle_id'] == vehicle].iloc[0]
            current_health = vehicle_data['battery_health_percent']
            current_cycles = vehicle_data['charging_cycles']
            
            for month in range(0, 25):  # 2 years forecast
                # Degradation model: ~2% per year + cycle degradation
                forecast_health = max(50, current_health - (month * 0.15) - (month * 10 * 0.01))
                forecast_data.append({
                    'vehicle_id': vehicle,
                    'month': month,
                    'battery_health': forecast_health
                })
        
        forecast_df = pd.DataFrame(forecast_data)
        
        fig = px.line(forecast_df, x='month', y='battery_health', color='vehicle_id',
                     title='2-Year Battery Health Forecast',
                     labels={'month': 'Months from Now', 'battery_health': 'Battery Health (%)'})
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation_text="Replacement Threshold")
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights
    st.markdown("### 🤖 AI-Powered Fleet Insights")
    
    if st.button("Generate Insights for Meera"):
        with st.spinner("Analyzing fleet data with Gemini AI..."):
            underperforming = (filtered_df['actual_range_km'] < filtered_df['predicted_range_km'] * 0.85).sum()
            
            prompt = f"""As a fleet manager, analyze this EV battery performance data:
            - Fleet size: {filtered_df['vehicle_id'].nunique()} vehicles
            - Average battery health: {filtered_df.groupby('vehicle_id')['battery_health_percent'].last().mean():.1f}%
            - Vehicles needing replacement: {(latest_data['needs_replacement'] == True).sum()}
            - Underperforming vehicles: {underperforming}
            - Best driving condition for range: {filtered_df.groupby('driving_condition')['actual_range_km'].mean().idxmax()}
            - Optimal temperature range: 20-25°C
            
            Provide 3-4 actionable insights for fleet optimization, maintenance scheduling,
            and cost reduction. Include recommendations for battery replacement timing."""
            
            insights = get_ai_insights(prompt)
            st.info(insights)

# ==================== SCENARIO 3: EV MODEL COMPARISON ====================

def scenario_ev_comparison():
    """Comparative EV Model Efficiency Dashboard"""
    
    st.markdown("## 🚗 Scenario 3: Comparative EV Model Efficiency Dashboard")
    st.markdown("*For Environmentally Conscious Consumers like Ravi*")
    
    df = generate_ev_models_data()
    
    # User Preferences
    st.markdown("### 🎯 Your Preferences")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        budget_max = st.slider("Maximum Budget ($)", 
                              min_value=20000, max_value=80000, 
                              value=50000, step=5000)
    with col2:
        min_range_required = st.slider("Minimum Range Required (km)",
                                      min_value=200, max_value=800,
                                      value=350, step=50)
    with col3:
        driving_style = st.selectbox(
            "Your Driving Style",
            options=['City Commuter', 'Highway Driver', 'Mixed Usage', 'Eco Conscious']
        )
    
    # Apply driving style adjustments
    style_multipliers = {
        'City Commuter': {'range': 0.85, 'efficiency': 1.0},
        'Highway Driver': {'range': 1.0, 'efficiency': 0.95},
        'Mixed Usage': {'range': 0.90, 'efficiency': 0.98},
        'Eco Conscious': {'range': 0.95, 'efficiency': 1.1}
    }
    
    multiplier = style_multipliers[driving_style]
    df['adjusted_range'] = (df['range_km'] * multiplier['range']).round(0)
    df['adjusted_efficiency'] = (df['efficiency_km_kwh'] * multiplier['efficiency']).round(2)
    
    # Filter based on preferences
    filtered_df = df[
        (df['price_usd'] <= budget_max) &
        (df['adjusted_range'] >= min_range_required)
    ]
    
    if len(filtered_df) == 0:
        st.warning("No EVs match your criteria. Try adjusting your filters.")
        return
    
    # Top Recommendations
    st.markdown("### 🏆 Top Recommendations for You")
    
    # Calculate overall score
    filtered_df = filtered_df.copy()
    filtered_df['value_score'] = (
        (filtered_df['adjusted_range'] / filtered_df['price_usd'] * 10000) * 0.3 +
        (filtered_df['adjusted_efficiency'] * 10) * 0.3 +
        (filtered_df['annual_savings_vs_ice'] / 1000) * 0.2 +
        (filtered_df['annual_co2_savings_kg'] / 100) * 0.2
    ).round(1)
    
    top_3 = filtered_df.nlargest(3, 'value_score')
    
    cols = st.columns(3)
    for idx, (_, row) in enumerate(top_3.iterrows()):
        with cols[idx]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 15px; color: white; text-align: center;">
                <h3 style="margin: 0; color: white;">#{idx+1} {row['model']}</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">{row['brand']}</p>
                <hr style="border-color: rgba(255,255,255,0.3);">
                <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">${row['price_usd']:,}</p>
                <p style="font-size: 0.9rem;">{row['adjusted_range']:.0f} km range</p>
                <p style="font-size: 0.9rem;">{row['adjusted_efficiency']:.1f} km/kWh</p>
                <p style="font-size: 1.2rem; font-weight: bold; color: #FCD34D;">Score: {row['value_score']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("### 📊 Comparison Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Cost Analysis", "🔋 Efficiency", "🌱 Environmental Impact", "📋 Detailed Comparison"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Price vs Range scatter
            fig = px.scatter(filtered_df, x='price_usd', y='adjusted_range',
                           size='battery_kwh', color='brand',
                           hover_data=['model', 'efficiency_km_kwh'],
                           title='Price vs Range (bubble size = battery capacity)')
            fig.update_xaxes(title='Price (USD)')
            fig.update_yaxes(title='Adjusted Range (km)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 5-Year TCO comparison
            fig = px.bar(filtered_df.nlargest(10, 'value_score'),
                        x='model', y='5year_tco',
                        color='5year_tco',
                        color_continuous_scale='RdYlGn_r',
                        title='5-Year Total Cost of Ownership (Top 10)')
            fig.update_xaxes(title='EV Model')
            fig.update_yaxes(title='5-Year TCO ($)')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Efficiency comparison
            fig = px.bar(filtered_df.sort_values('adjusted_efficiency', ascending=True).tail(10),
                        x='adjusted_efficiency', y='model', orientation='h',
                        color='adjusted_efficiency',
                        color_continuous_scale='Viridis',
                        title='Energy Efficiency (km/kWh)')
            fig.update_xaxes(title='Efficiency (km/kWh)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cost per km
            fig = px.scatter(filtered_df, x='adjusted_range', y='cost_per_km',
                           size='price_usd', color='category',
                           hover_data=['model'],
                           title='Range vs Cost per km')
            fig.update_xaxes(title='Adjusted Range (km)')
            fig.update_yaxes(title='Cost per km ($)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Annual savings vs ICE
            fig = px.bar(filtered_df.nlargest(10, 'annual_savings_vs_ice'),
                        x='model', y='annual_savings_vs_ice',
                        color='annual_savings_vs_ice',
                        color_continuous_scale='Greens',
                        title='Annual Savings vs ICE Vehicle (Top 10)')
            fig.update_xaxes(title='EV Model')
            fig.update_yaxes(title='Annual Savings ($)')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # CO2 savings over time
            years = list(range(1, 11))
            co2_data = []
            
            for _, row in filtered_df.nlargest(5, 'annual_co2_savings_kg').iterrows():
                for year in years:
                    co2_data.append({
                        'model': row['model'],
                        'year': year,
                        'cumulative_co2_saved': row['annual_co2_savings_kg'] * year
                    })
            
            co2_df = pd.DataFrame(co2_data)
            
            fig = px.line(co2_df, x='year', y='cumulative_co2_saved', color='model',
                         title='Cumulative CO2 Savings Over 10 Years',
                         labels={'year': 'Years', 'cumulative_co2_saved': 'CO2 Saved (kg)'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Detailed comparison table
        comparison_cols = ['model', 'brand', 'price_usd', 'adjusted_range', 
                          'adjusted_efficiency', 'charging_time_h', 
                          'annual_savings_vs_ice', '5year_tco', 'value_score']
        
        display_df = filtered_df[comparison_cols].sort_values('value_score', ascending=False)
        display_df.columns = ['Model', 'Brand', 'Price ($)', 'Range (km)', 
                             'Efficiency (km/kWh)', 'Charge Time (h)',
                             'Annual Savings ($)', '5Y TCO ($)', 'Score']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Custom comparison
        st.markdown("#### 🔄 Compare Specific Models")
        
        col1, col2 = st.columns(2)
        with col1:
            model1 = st.selectbox("Select Model 1", filtered_df['model'].values, key='m1')
        with col2:
            model2 = st.selectbox("Select Model 2", filtered_df['model'].values, key='m2', index=min(1, len(filtered_df)-1))
        
        if model1 and model2:
            m1_data = filtered_df[filtered_df['model'] == model1].iloc[0]
            m2_data = filtered_df[filtered_df['model'] == model2].iloc[0]
            
            comparison_metrics = ['price_usd', 'adjusted_range', 'adjusted_efficiency', 
                                 'charging_time_h', 'annual_savings_vs_ice', '5year_tco']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=[m1_data[m] for m in comparison_metrics],
                theta=['Price', 'Range', 'Efficiency', 'Charge Time', 'Annual Savings', '5Y TCO'],
                fill='toself',
                name=model1
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=[m2_data[m] for m in comparison_metrics],
                theta=['Price', 'Range', 'Efficiency', 'Charge Time', 'Annual Savings', '5Y TCO'],
                fill='toself',
                name=model2
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Model Comparison Radar Chart (normalized)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # AI Insights
    st.markdown("### 🤖 AI-Powered Buying Guide")
    
    if st.button("Get Personalized Recommendations for Ravi"):
        with st.spinner("Generating personalized insights with Gemini AI..."):
            top_pick = filtered_df.nlargest(1, 'value_score').iloc[0]
            
            prompt = f"""As an EV buying advisor, help a consumer with these preferences:
            - Budget: Up to ${budget_max:,}
            - Minimum range needed: {min_range_required} km
            - Driving style: {driving_style}
            - Top recommendation: {top_pick['model']} (${top_pick['price_usd']:,})
            
            Available options in budget: {len(filtered_df)} models
            
            Provide 3-4 personalized recommendations for choosing the right EV.
            Include considerations for charging infrastructure, total cost of ownership,
            and environmental impact. Address the specific driving style preference."""
            
            insights = get_ai_insights(prompt)
            st.info(insights)

# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    
    # Header
    st.markdown("<h1 class='main-header'>🚗 EV Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Comprehensive Electric Vehicle Data Analytics Platform</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Navigation")
        st.markdown("---")
        
        scenario = st.radio(
            "Select Scenario",
            options=[
                "🏠 Scenario 1: Charging Pattern Analysis",
                "🔋 Scenario 2: Battery Performance",
                "🚗 Scenario 3: EV Model Comparison"
            ]
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This dashboard provides comprehensive analytics for:
        
        **Scenario 1** - City energy planners managing EV charging infrastructure
        
        **Scenario 2** - Fleet managers optimizing battery performance
        
        **Scenario 3** - Consumers comparing EV models
        
        Powered by **Gemini AI** for intelligent insights.
        """)
        
        st.markdown("---")
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input("Gemini API Key", type="password", 
                               value=os.getenv("GEMINI_API_KEY", ""))
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            global gemini_model
            try:
                genai.configure(api_key=api_key)
                gemini_model = genai.GenerativeModel(_resolve_gemini_model_name())
                st.success("✅ API Key configured!")
            except Exception as e:
                st.error(f"Failed to configure API: {e}")
    
    # Route to appropriate scenario
    if "Scenario 1" in scenario:
        scenario_charging_analysis()
    elif "Scenario 2" in scenario:
        scenario_battery_performance()
    else:
        scenario_ev_comparison()
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #6B7280;'>EV Analytics Dashboard © 2024 | Built with Streamlit & Gemini AI</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
