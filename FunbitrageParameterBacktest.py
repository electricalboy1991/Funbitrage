import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

# 데이터 로드
df = pd.read_excel("C:/Users/world/PycharmProjects/Funbitrage/GPT용3.xlsx")

# date 열을 datetime 형식으로 변환
df['date'] = pd.to_datetime(df['date'])

# '무기한' 데이터에서 중복된 날짜 제거 (가장 최신 데이터 사용)
unique_dates = df.sort_values(by='date').drop_duplicates(subset='date', keep='last')

# Dash 애플리케이션 생성
app = dash.Dash(__name__)

# 유니크한 심볼 리스트 생성
symbols = df['symbol'].unique()

# Dash 레이아웃 설정
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[
    html.H1(children='펀비트라지 분석', style={'flex': '0 1 auto'}),

    html.Div([
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': s, 'value': s} for s in symbols],
            multi=True,
            placeholder='심볼을 선택하세요'
        )
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


@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('symbol-dropdown', 'value')]
)
def update_graph(selected_symbols):
    data = []

    # 초기 로드 시 모든 심볼 데이터를 플롯
    if not selected_symbols:
        selected_symbols = symbols

    filtered_df = df[df['symbol'].isin(selected_symbols)]

    for symbol in selected_symbols:
        symbol_df = filtered_df[filtered_df['symbol'] == symbol]

        # 각 symbol의 첫날과 첫날로부터 181일 후의 날짜
        first_date = symbol_df['date'].min()
        end_date = first_date + pd.Timedelta(days=181)

        # 진입 점선 추가
        data.append(go.Scatter(
            x=[first_date, end_date],
            y=[5, 0],
            mode='lines',
            name=f'{symbol} 진입 점선',
            line=dict(dash='dot', color='blue')
        ))

        # 청산 점선 추가
        data.append(go.Scatter(
            x=[first_date, end_date],
            y=[8, 0],
            mode='lines',
            name=f'{symbol} 청산 점선',
            line=dict(dash='dot', color='red')
        ))

        data.append(go.Scatter(
            x=symbol_df['date'],
            y=symbol_df['괴리율'],
            mode='lines',
            name=f'{symbol} 괴리율',
            yaxis='y1'
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
    }


# 서버 실행
if __name__ == '__main__':
    app.run_server(debug=True)
