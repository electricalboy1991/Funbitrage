import requests
import pandas as pd
from datetime import datetime, timedelta

# 바이낸스 API를 사용하여 데이터 가져오기
def get_binance_data(symbol, interval, start_str, end_str, base_url='https://dapi.binance.com'):
    start_date = datetime.strptime(start_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_str, '%Y-%m-%d')
    delta = timedelta(days=200)  # 최대 200일씩 나눠서 요청
    
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
            'limit': 1500  # 1500개의 데이터 포인트 요청
        }
        
        response = requests.get(f'{base_url}/dapi/v1/klines', params=params)
        data = response.json()
        
        # 데이터가 없거나 에러가 발생한 경우 처리
        if response.status_code != 200 or not data:
            print(f"Error fetching data for {symbol} from {start_date} to {current_end_date}: {response.text}")
            start_date = current_end_date  # 다음 구간으로 이동
            continue
        
        all_data.extend(data)
        start_date = current_end_date
    
    if not all_data:
        return pd.DataFrame()  # 빈 DataFrame 반환
    
    return pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ]).astype({'timestamp': 'int64', 'open': 'float64', 'high': 'float64', 'low': 'float64', 'close': 'float64', 'volume': 'float64'})

# 데이터 수집
symbol_perpetual = 'BTCUSD_PERP'
start_date = '2019-01-01'
end_date = '2024-10-27'

df_perpetual = get_binance_data(symbol_perpetual, '1d', start_date, end_date)

# 데이터가 비어 있는지 확인
if df_perpetual.empty:
    print("No data found. Please check the symbol and the date range.")
else:
    # 날짜 변환
    df_perpetual['date'] = pd.to_datetime(df_perpetual['timestamp'], unit='ms')
    df_perpetual = df_perpetual[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    # 엑셀 파일로 저장
    df_perpetual.to_excel('BTCUSD_PERP_2019_2024.xlsx', index=False)
    print("Data has been successfully saved to BTCUSD_PERP_2019_2024.xlsx")
