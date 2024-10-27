import requests
import pandas as pd
from datetime import datetime, timedelta

# 바이낸스 API를 사용하여 데이터 가져오기
def get_binance_data(symbol, interval, start_str, end_str, base_url='https://dapi.binance.com'):
    start_date = datetime.strptime(start_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_str, '%Y-%m-%d')
    delta = timedelta(days=30)  # 30일씩 나눠서 요청
    
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
        if len(data) < 1500:  # 데이터가 1500개 미만이면 마지막 데이터를 가져왔음을 의미
            break
    
    if not all_data:
        return pd.DataFrame()  # 빈 DataFrame 반환
    
    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ]).astype({
        'timestamp': 'int64', 'open': 'float64', 'high': 'float64', 'low': 'float64', 
        'close': 'float64', 'volume': 'float64'
    })
    
    return df

# 심볼 설정
symbol_perpetual = 'BTCUSD_PERP'

# 날짜 설정: 최근 6개월
end_date = datetime.utcnow().strftime('%Y-%m-%d')
start_date = (datetime.utcnow() - timedelta(days=180)).strftime('%Y-%m-%d')

print(f"Fetching data for {symbol_perpetual} from {start_date} to {end_date}")

# 데이터를 가져오기
df = get_binance_data(symbol_perpetual, '5m', start_date, end_date)

if df.empty:
    print("No data found for the given symbol and date range.")
else:
    # 날짜 변환 및 데이터 확인
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    print(f"Total records fetched: {len(df)}")
    print(df.head())
    print(df.tail())
