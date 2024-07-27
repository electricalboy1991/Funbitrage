import pandas as pd
import plotly.graph_objects as go

# Load the data
file_path = 'C:/Users/world/PycharmProjects/Funbitrage/GPT용3.xlsx'
data = pd.read_excel(file_path)

# Convert the date column to datetime format
data['date'] = pd.to_datetime(data['date'])

# Get the unique symbols
symbols = data['symbol'].unique()

# Create a plotly figure
fig = go.Figure()

# Initialize lists to store values at day 1 and day 92
day_1_values = []
day_92_values = []

# Add a trace for each symbol
for symbol in symbols:
    symbol_data = data[data['symbol'] == symbol].sort_values(by='date')
    days = (symbol_data['date'] - symbol_data['date'].min()).dt.days + 1

    # Collect values for day 1 and day 92, excluding BTCUSD_241227

    day_1_value = symbol_data[symbol_data['date'] == symbol_data['date'].min()]['괴리율'].values
    if len(day_1_value) > 0:
        day_1_values.append(day_1_value[0])

    day_92_value = symbol_data[(symbol_data['date'] - symbol_data['date'].min()).dt.days == 91]['괴리율'].values
    if len(day_92_value) > 0:
        day_92_values.append(day_92_value[0])

    fig.add_trace(go.Scatter(x=days, y=symbol_data['괴리율'], mode='lines', name=symbol))


day_1_values.pop()

# Calculate mean, median, and standard deviation for day 1 and day 92
mean_day_1 = sum(day_1_values) / len(day_1_values) if day_1_values else 0
std_dev_day_1 = (sum((x - mean_day_1) ** 2 for x in day_1_values) / len(day_1_values)) ** 0.5 if day_1_values else 0
median_day_1 = sorted(day_1_values)[len(day_1_values) // 2] if day_1_values else 0

mean_day_92 = sum(day_92_values) / len(day_92_values) if day_92_values else 0
std_dev_day_92 = (sum((x - mean_day_92) ** 2 for x in day_92_values) / len(day_92_values)) ** 0.5 if day_92_values else 0
median_day_92 = sorted(day_92_values)[len(day_92_values) // 2] if day_92_values else 0

# Update layout for better visualization
fig.update_layout(
    title='괴리율 Line Chart for Each Symbol',
    xaxis_title='Days',
    yaxis_title='괴리율',
    legend_title='Symbols',
    hovermode='x unified',
    annotations=[
        dict(
            x=1,
            y=max(max(day_1_values, default=0), max(day_92_values, default=0)) * 1.05 if day_1_values and day_92_values else 0,
            xref="x",
            yref="y",
            text=f"Median: {median_day_1:.2f}, Mean: {mean_day_1:.2f}, Std Dev: {std_dev_day_1:.2f}",
            showarrow=False,
            font=dict(
                color="RoyalBlue",
                size=17
            ),
        ),
        dict(
            x=92,
            y=max(max(day_1_values, default=0), max(day_92_values, default=0)) * 1.05 if day_1_values and day_92_values else 0,
            xref="x",
            yref="y",
            text=f"Median: {median_day_92:.2f}, Mean: {mean_day_92:.2f}, Std Dev: {std_dev_day_92:.2f}",
            showarrow=False,
            font=dict(
                color="RoyalBlue",
                size=17
            ),
        )
    ],
    shapes=[
        dict(
            type="line",
            x0=1,
            y0=0,
            x1=1,
            y1=max(max(day_1_values, default=0), max(day_92_values, default=0)) if day_1_values and day_92_values else 0,
            line=dict(
                color="RoyalBlue",
                width=2,
                dash="dashdot",
            ),
        ),
        dict(
            type="line",
            x0=92,
            y0=0,
            x1=92,
            y1=max(max(day_1_values, default=0), max(day_92_values, default=0)) if day_1_values and day_92_values else 0,
            line=dict(
                color="RoyalBlue",
                width=2,
                dash="dashdot",
            ),
        )
    ]
)

# Show the interactive plot
fig.show()
