import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

# Load the data
file_path = 'C:/Users/world/PycharmProjects/Funbitrage/GPT용3.xlsx'
data = pd.read_excel(file_path)

# Convert the date column to datetime format
data['date'] = pd.to_datetime(data['date'])

# Get the unique symbols
symbols = data['symbol'].unique()

# Prepare data for plotting
plot_data = []
for symbol in symbols:
    symbol_data = data[data['symbol'] == symbol].sort_values(by='date')
    days = (symbol_data['date'] - symbol_data['date'].min()).dt.days + 1
    plot_data.append(go.Scatter(x=days, y=symbol_data['괴리율'], mode='lines', name=symbol))

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    dcc.Store(id='hidden-data', data={'visible_traces': [True]*len(plot_data)}),
    html.Div([
        dcc.Graph(id='line-chart', style={'height': '90vh'}),
    ], style={'width': '80%', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        html.Label('Day 1 진입 괴리율 라인:'),
        dcc.Slider(id='slider-1', min=0, max=10, step=0.1, value=5, marks={i: str(i) for i in range(0, 11, 2)}),
        html.Div(id='slider-1-output', style={'margin-bottom': '20px'}),
        html.Label('Day 1 청산 괴리율 라인 및 다음 물 이연:'),
        dcc.Slider(id='slider-2', min=0, max=10, step=0.1, value=7, marks={i: str(i) for i in range(0, 11, 2)}),
        html.Div(id='slider-2-output', style={'margin-bottom': '20px'}),
        html.Label('Day 1 다음 물 없어도 청산 라인:'),
        dcc.Slider(id='slider-3', min=0, max=10, step=0.1, value=8, marks={i: str(i) for i in range(0, 11, 2)}),
        html.Div(id='slider-3-output', style={'margin-bottom': '20px'}),
        html.Label('I-I 모양 자 위치 (시작일):'),
        dcc.Slider(id='slider-i', min=1, max=92, step=1, value=1, marks={i: str(i) for i in range(1, 93, 10)}),
        html.Div(id='slider-i-output', style={'margin-bottom': '20px'}),
        html.Label('I-I 모양 자 위치 (Y축):'),
        dcc.Slider(id='slider-i-y', min=-1, max=14, step=0.1, value=0, marks={i: str(i) for i in range(-1, 15, 2)}),
        html.Div(id='slider-i-y-output', style={'margin-bottom': '20px'}),
    ], style={'width': '20%', 'display': 'inline-block', 'padding': '20px', 'vertical-align': 'top', 'position': 'absolute', 'right': '0px', 'top': '70vh'})
])

@app.callback(
    Output('line-chart', 'figure'),
    [Input('slider-1', 'value'),
     Input('slider-2', 'value'),
     Input('slider-3', 'value'),
     Input('slider-i', 'value'),
     Input('slider-i-y', 'value')],
    [State('hidden-data', 'data')]
)
def update_lines(val1, val2, val3, i_val, i_y_val, hidden_data):
    fig = go.Figure()

    # Add traces and set visibility based on stored data
    for trace, visible in zip(plot_data, hidden_data['visible_traces']):
        trace.visible = visible
        fig.add_trace(trace)

    fig.add_trace(go.Scatter(x=[1, 182], y=[val1, 0], mode='lines', line=dict(dash='dot', color='black'), name='진입 괴리율 라인'))
    fig.add_trace(go.Scatter(x=[1, 182], y=[val2, 0], mode='lines', line=dict(dash='dashdot', color='dimgray'), name='청산 괴리율 라인 및 다음 물 이연'))
    fig.add_trace(go.Scatter(x=[1, 182], y=[val3, 0], mode='lines', line=dict(dash='dash', color='gray'), name='다음 물 없어도 청산 라인'))

    # Add the I-I shape
    fig.add_shape(
        type='line',
        x0=i_val,
        y0=i_y_val,
        x1=i_val + 91,
        y1=i_y_val,
        line=dict(color='blue', width=4)  # 두께를 2배로 증가
    )

    # Update layout for better visualization
    fig.update_layout(
        title='괴리율 Line Chart for Each Symbol',
        xaxis_title='Days',
        yaxis_title='괴리율',
        legend_title='Symbols',
        hovermode='x unified',
    )

    return fig

@app.callback(
    Output('hidden-data', 'data'),
    [Input('line-chart', 'relayoutData')],
    [State('hidden-data', 'data')]
)
def store_trace_visibility(relayoutData, hidden_data):
    if relayoutData:
        for key in relayoutData:
            if 'legend' in key and 'item' in key and 'visible' in relayoutData[key]:
                index = int(key.split('[')[1].split(']')[0])
                hidden_data['visible_traces'][index] = relayoutData[key]['visible'] == 'legendonly'
    return hidden_data

@app.callback(
    [Output('slider-1-output', 'children'),
     Output('slider-2-output', 'children'),
     Output('slider-3-output', 'children'),
     Output('slider-i-output', 'children'),
     Output('slider-i-y-output', 'children')],
    [Input('slider-1', 'value'),
     Input('slider-2', 'value'),
     Input('slider-3', 'value'),
     Input('slider-i', 'value'),
     Input('slider-i-y', 'value')]
)
def update_slider_outputs(val1, val2, val3, i_val, i_y_val):
    return f'Current Value: {val1}', f'Current Value: {val2}', f'Current Value: {val3}', f'I-I 모양 자 시작일: {i_val}일', f'I-I 모양 자 Y축: {i_y_val}'

if __name__ == '__main__':
    app.run_server(debug=True)
