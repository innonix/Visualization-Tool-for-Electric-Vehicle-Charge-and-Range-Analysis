# EV Analytics Dashboard

A comprehensive Streamlit application for Electric Vehicle (EV) data analytics with three distinct scenarios, powered by Gemini AI for intelligent insights.

## 🚗 Features

### Scenario 1: Charging Pattern & Usage Analysis
**For City Energy Planners (like Aarav)**

- Analyze charging sessions by time of day, neighborhood, and station type
- Identify peak charging hours and grid demand patterns
- Visualize geographic distribution of charging demand
- Track revenue and cost analysis by user type
- AI-powered insights for infrastructure planning

**Key Metrics:**
- Total charging sessions and energy consumption
- Peak hour demand analysis
- Neighborhood heatmaps
- Monthly and daily usage trends

### Scenario 2: Battery Performance vs Driving Range
**For Fleet Managers (like Meera)**

- Monitor battery health across entire fleet
- Track state of charge, depth of discharge, and charging cycles
- Analyze efficiency under different driving conditions
- Predict battery replacement needs
- Temperature impact analysis

**Key Metrics:**
- Fleet-wide battery health percentage
- Vehicles needing replacement
- Predicted vs actual range comparison
- 2-year battery degradation forecast

### Scenario 3: Comparative EV Model Efficiency Dashboard
**For Environmentally Conscious Consumers (like Ravi)**

- Compare EV models by price, range, efficiency, and environmental impact
- Calculate total cost of ownership (TCO)
- Estimate annual savings vs ICE vehicles
- CO2 savings calculations
- Personalized recommendations based on driving style

**Key Metrics:**
- Price per km of range
- Energy efficiency (km/kWh)
- 5-year TCO comparison
- Annual CO2 savings

## 🤖 AI Integration

The dashboard integrates with Google's Gemini AI to provide:
- Personalized buying recommendations
- Fleet optimization insights
- Infrastructure planning advice
- Data-driven decision support

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone or download the repository:
```bash
cd ev_analytics_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure Gemini API:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Running the App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📊 Data Sources

The application uses synthetic data generated for demonstration purposes:
- **Charging Data**: 5,000 simulated charging sessions across 7 neighborhoods
- **Battery Data**: 10,000 records from 150 vehicles
- **EV Models**: 15 popular electric vehicle models with real specifications

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Google Generative AI**: Gemini AI integration

## 📁 Project Structure

```
ev_analytics_app/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Configuration

### Gemini AI Setup

To enable AI-powered insights:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable: `export GEMINI_API_KEY="your_key"`
3. Or enter the key in the sidebar when running the app

## 📝 Usage Tips

1. **Navigation**: Use the sidebar to switch between scenarios
2. **Filters**: Each scenario has interactive filters to customize the view
3. **Visualizations**: Click and drag to zoom, double-click to reset
4. **AI Insights**: Click the "Generate Insights" button for AI analysis
5. **Data Tables**: Scroll and sort tables for detailed analysis

## 🌟 Key Features

- **Interactive Dashboards**: Filter and explore data in real-time
- **Multiple Visualization Types**: Bar charts, line graphs, scatter plots, heatmaps, radar charts
- **Responsive Design**: Works on desktop and mobile devices
- **Export Ready**: Data tables can be copied for further analysis

## 📄 License

This project is open source and available for educational and demonstration purposes.

## 🤝 Contributing

Feel free to fork and modify the code for your own use cases. The modular structure makes it easy to:
- Add new scenarios
- Integrate real data sources
- Customize visualizations
- Extend AI capabilities
