import requests
import pandas as pd
from datetime import datetime, timedelta

# 바이낸스 API를 사용하여 데이터 가져오기
def get_binance_data(symbol, interval, start_str, end_str, base_url):
    start_date = datetime.strptime(start_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_str, '%Y-%m-%d')
    delta = timedelta(days=200)
    
    all_data = []
    
    while start_date < end_date:
        current_end_date = min(start_date + delta, end_date)
        start_time = int(start_date.timestamp() * 1000)
        end_time = int(current_end_date.timestamp() * 1000)
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': 1000
        }
        
        response = requests.get(f'{base_url}/dapi/v1/klines', params=params)
        data = response.json()
        
        if response.status_code != 200 or not data:
            print(f"Error fetching data for {symbol}: {response.text}")
            break
        
        all_data.extend(data)
        start_date = current_end_date
    
    if not all_data:
        return pd.DataFrame()  # Empty DataFrame
    
    return pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ]).astype({'timestamp': 'int64', 'open': 'float64', 'high': 'float64', 'low': 'float64', 'close': 'float64', 'volume': 'float64'})

# 데이터 수집
base_url = 'https://dapi.binance.com'
symbol_semi_annual = 'BTCUSD_250328'  # 2023년 12월 29일에 만료되는 반기 선물 심볼
start_date = '2024-09-28'
end_date = '2024-10-26'

df_semi_annual = get_binance_data(symbol_semi_annual, '1d', start_date, end_date, base_url)

# 데이터가 비어 있는지 확인
if df_semi_annual.empty:
    print("No data found. Please check the symbol and the date range.")
else:
    # 날짜 변환
    df_semi_annual['date'] = pd.to_datetime(df_semi_annual['timestamp'], unit='ms')
    df_semi_annual = df_semi_annual[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    # 엑셀 파일로 저장
    df_semi_annual.to_excel('BTCUSD_250328.xlsx', index=False)
    print("Data has been successfully saved to BTCUSD_250328.xlsx")
