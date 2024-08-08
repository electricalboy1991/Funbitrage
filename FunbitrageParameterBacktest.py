import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

# 데이터 로드
df = pd.read_excel("C:/Users/world/PycharmProjects/Funbitrage/GPT용3.xlsx")

# date 열을 datetime 형식으로 변환
df['date'] = pd.to_datetime(df['date'])

# Dash 애플리케이션 생성
app = dash.Dash(__name__)

# 유니크한 심볼 리스트를 가장 과거 날짜 순서로 정렬
symbols_sorted = df.groupby('symbol')['date'].min().sort_values().index

# 전체 포지션 기간 계산 및 수식 계산
def calculate_total_position_duration_and_formula(positions):
    total_duration = 0
    total_formula_value = 1  # 누적 곱 수익률을 1로 초기화

    for position in positions:
        duration = (position['exit_date'] - position['entry_date']).days
        entry_value = position['entry_y']
        exit_value = position['exit_y']
        formula_value = 0.03 * duration + (exit_value - entry_value) - 0.1

        # 누적 곱 수익률 계산 (1 + 0.01 * formula_value)
        total_formula_value *= (1 + 18*0.01 * formula_value)

        total_duration += duration

    return total_duration, 100*(total_formula_value-1)

# Dash 레이아웃 설정
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div(children=[
            html.H1(id='formula-value', style={'flex': '0 1 auto', 'display': 'inline-block'}),
            html.Span("% 레버리지18배*[0.01*3*일수+(청산-진입)-0.035*2(수수료*2)-0.03(슬리피지 등)]", style={'font-size': '70%', 'margin-left': '10px', 'vertical-align': 'middle'})
        ]),
        html.H2(id='position-duration', style={'flex': '0 1 auto', 'margin': 'auto 0'})
    ]),

    html.Div([
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': s, 'value': s} for s in symbols_sorted],
            value=symbols_sorted.tolist(),  # 처음 실행할 때 모든 심볼이 선택된 상태로 설정
            multi=True,
            placeholder='심볼을 선택하세요'
        ),
        html.Div(id='slider-container', style={'margin-top': '10px'}, children=[
            html.Label('청산 점선 기준값:', style={'margin-right': '10px'}),
            dcc.Slider(
                id='exit-threshold-slider',
                min=5,
                max=15,
                step=0.1,
                value=10,
                marks={i: str(i) for i in range(5, 16)}
            ),
            html.Div(id='slider-value', style={'margin-left': '20px', 'display': 'inline-block'})
        ]),
        html.Div(id='entry-slider-container', style={'margin-top': '10px'}, children=[
            html.Label('진입 점선 기준값:', style={'margin-right': '10px'}),
            dcc.Slider(
                id='entry-threshold-slider',
                min=3,
                max=7,
                step=0.1,
                value=5,
                marks={i: str(i) for i in range(0, 11)}
            ),
            html.Div(id='entry-slider-value', style={'margin-left': '20px', 'display': 'inline-block'})
        ])
    ], style={'margin-bottom': '10px', 'flex': '0 1 auto'}),

    html.Div(
        dcc.Graph(
            id='example-graph',
            config={
                'scrollZoom': True
            },
            style={'height': '100%'}
        ),
        style={'flex': '1 1 auto'}
    )
])

def perform_backtest(symbols, df, entry_threshold, exit_threshold):
    positions = []
    current_position_end = None

    for symbol in symbols:
        symbol_df = df[df['symbol'] == symbol].sort_values(by='date')

        first_date = symbol_df['date'].min()
        end_date = first_date + pd.Timedelta(days=181)
        expiry_date = symbol_df['date'].max()

        entry_slope = -entry_threshold / 181  # y2 - y1 / x2 - x1 for entry line
        exit_slope = -exit_threshold / 181  # y2 - y1 / x2 - x1 for exit line

        symbol_df['진입 점선'] = entry_threshold + entry_slope * (symbol_df['date'] - first_date).dt.days
        symbol_df['청산 점선'] = exit_threshold + exit_slope * (symbol_df['date'] - first_date).dt.days

        for i in range(len(symbol_df)):
            current_date = symbol_df.iloc[i]['date']
            if current_position_end and current_date <= current_position_end:
                continue  # 이미 포지션이 열려있는 동안 다른 포지션을 잡지 않음

            if symbol_df.iloc[i]['괴리율'] < symbol_df.iloc[i]['진입 점선']:
                entry_date = current_date
                exit_dates = symbol_df[(symbol_df['date'] > entry_date) & (symbol_df['괴리율'] > symbol_df['청산 점선'])]['date']
                exit_date = exit_dates.min() if not exit_dates.empty else expiry_date
                entry_y = symbol_df[symbol_df['date'] == entry_date]['괴리율'].values[0] if not symbol_df[symbol_df['date'] == entry_date].empty else 0
                exit_y = symbol_df[symbol_df['date'] == exit_date]['괴리율'].values[0] if not symbol_df[symbol_df['date'] == exit_date].empty else 0

                positions.append({
                    'symbol': symbol,
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_line': {'x': [first_date, end_date], 'y': [entry_threshold, 0]},
                    'exit_line': {'x': [first_date, end_date], 'y': [exit_threshold, 0]},
                    'entry_y': entry_y,
                    'exit_y': exit_y
                })

                current_position_end = exit_date  # 포지션이 끝나는 시점을 업데이트
                break  # 한 번 진입하면 다음 진입을 위해 루프를 종료

    return positions

@app.callback(
    [dash.dependencies.Output('example-graph', 'figure'),
     dash.dependencies.Output('position-duration', 'children'),
     dash.dependencies.Output('slider-value', 'children'),
     dash.dependencies.Output('entry-slider-value', 'children'),
     dash.dependencies.Output('formula-value', 'children')],
    [dash.dependencies.Input('symbol-dropdown', 'value'),
     dash.dependencies.Input('exit-threshold-slider', 'value'),
     dash.dependencies.Input('entry-threshold-slider', 'value')]
)
def update_graph(selected_symbols, exit_threshold, entry_threshold):
    data = []

    if not selected_symbols:
        selected_symbols = symbols_sorted

    positions = perform_backtest(selected_symbols, df, entry_threshold, exit_threshold)
    total_position_duration, total_formula_value = calculate_total_position_duration_and_formula(positions)
    filtered_df = df[df['symbol'].isin(selected_symbols)]

    for position in positions:
        symbol_df = filtered_df[filtered_df['symbol'] == position['symbol']]

        data.append(go.Scatter(
            x=position['entry_line']['x'],
            y=position['entry_line']['y'],
            mode='lines',
            name=f'{position["symbol"]} 진입 점선',
            line=dict(dash='dot', color='blue')
        ))

        data.append(go.Scatter(
            x=position['exit_line']['x'],
            y=position['exit_line']['y'],
            mode='lines',
            name=f'{position["symbol"]} 청산 점선',
            line=dict(dash='dot', color='red')
        ))

        data.append(go.Scatter(
            x=symbol_df['date'],
            y=symbol_df['괴리율'],
            mode='lines',
            name=f'{position["symbol"]} 괴리율',
            yaxis='y1'
        ))

        # 포지션 잡혀있는 구간 색칠
        entry_y_value = symbol_df[symbol_df['date'] == position['entry_date']]['괴리율'].values[0] if not symbol_df[symbol_df['date'] == position['entry_date']].empty else 0
        exit_y_value = symbol_df[symbol_df['date'] == position['exit_date']]['괴리율'].values[0] if not symbol_df[symbol_df['date'] == position['exit_date']].empty else 0

        data.append(go.Scatter(
            x=[position['entry_date'], position['exit_date']],
            y=[entry_y_value, exit_y_value],
            fill='tozeroy',
            fillcolor='rgba(0, 0, 255, 0.2)',
            mode='none',
            name=f'{position["symbol"]} 포지션'
        ))

        # 진입, 청산 지점 표시
        data.append(go.Scatter(
            x=[position['entry_date']],
            y=[entry_y_value],
            mode='markers',
            marker=dict(symbol='star', size=10, color='blue'),
            name=f'{position["symbol"]} 진입 지점'
        ))

        data.append(go.Scatter(
            x=[position['exit_date']],
            y=[exit_y_value],
            mode='markers',
            marker=dict(symbol='star', size=10, color='red'),
            name=f'{position["symbol"]} 청산 지점'
        ))

    return {
        'data': data,
        'layout': go.Layout(
            title='펀비트라지 분석',
            xaxis=dict(title='날짜'),
            yaxis=dict(
                title='괴리율 (%)',
                side='left'
            ),
            yaxis2=dict(
                title='괴리율 (%)',
                overlaying='y',
                side='right'
            ),
            hovermode='closest',
            showlegend=True
        )
    }, f"Position 기간 : {total_position_duration}일", f"{exit_threshold}", f"{entry_threshold}", f"수익률: {total_formula_value:.2f} %"

# 서버 실행
if __name__ == '__main__':
    app.run_server(debug=True)
