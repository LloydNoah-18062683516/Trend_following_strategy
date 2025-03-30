import requests
import time
import pandas as pd
pd.set_option('expand_frame_repr',False)

# BASE_URL='https://api.binance.com'
#
# kline='/api/v1/klines'
#
# kline_url=BASE_URL+kline+'?'+'symbol=BTCUSDT&interval=1h&limit=1000'
# print(kline_url)
# resp=requests.get(kline_url)
# print(resp.json())
# df=pd.DataFrame(resp.json())
# print(df)
# exit()

# get data of the past year in Binance
BASE_URL='https://api.binance.com'
limit=1000
end_time=int(time.time()//60*60*1000)
print(end_time)
start_time=int(end_time-limit*60*1000)
print(start_time)

while True:
    url=BASE_URL+'/api/v1/klines'+'?symbol=BTCUSDT&interval=1m&limit='+str(limit)+'&startTime='+str(start_time)+'&endTime='+str(end_time)
    resp=requests.get(url)
    print(url)
    data=resp.json()
    df=pd.DataFrame(data,
                    columns={'open_time':0,'open':1,'high':2,'low':3,'close':4,'volume':5,
                             'close_time':6,'quote_volume':7,'trades':8,'taker_base_volume':9,
                             'taker_quote_volume':10,'ignore':11})
    df.set_index('open_time',inplace=True)
    df.to_csv(str(end_time) + '.csv')
    print(df)

    if len(df)<1000:
        break
    end_time=start_time
    start_time=int(end_time-limit*60*1000)
