import pandas as pd
import pyodbc
import os
from sqlalchemy import create_engine,text
import json
import urllib.parse
from datetime import datetime
from curl_cffi import requests
import time
import plotly
import plotly.express

def connect_sql_server():
    #load_dotenv('./.env')
    SERVER_DB = os.getenv('SERVER')
    DB=os.getenv("DATABASE")
    USER = os.getenv("USERNAME")
    PWD = os.getenv("PASSWORD")
    
    connstring="DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection=no".format(SERVER_DB,DB,USER,PWD)
    print(connstring)
    
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(connstring))
    conn = engine.connect()
    return conn
    
def build_payload(keywords, timeframe='today 5-y', geo='ID'):
    token_payload = {
        'hl': 'id-ID',
        'tz': '0',
        'req': {
            'comparisonItem': [{'keyword': keyword, 'time': timeframe, 'geo': geo} for keyword in keywords],
            'category': 0,
            'property': ''
        }
    }
    token_payload['req'] = json.dumps(token_payload['req'])
    return token_payload

def convert_to_desired_format(keywords,raw_data):
    import pandas as pd
    trend_data = {}
    cols=['periode','nama_perusahaan','trend_value']
    datas=[]
    for entry in raw_data['default']['timelineData']:
        timestamp = int(entry['time'])
        date_time_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        values =entry['value']
        idx=0
        for value in values:
            datas.append([date_time_str]+[keywords[idx]]+[value])
            idx+=1
    df=pd.DataFrame(datas, columns=cols)
    return df

# Cookies
def get_google_cookies(impersonate_version='chrome110'):
    with requests.Session() as session:
        session.get("https://www.google.com", impersonate=impersonate_version)
        return session.cookies

def fetch_trends_data(keywords, days_ago=7, geo='ID', hl='en-US', max_retries=5, browser_version='chrome110', browser_switch_retries=4):
    browser_versions = ['chrome110', 'edge101', 'chrome107', 'chrome104', 'chrome100', 'chrome101', 'chrome99']
    current_browser_version_index = browser_versions.index(browser_version)
    cookies = get_google_cookies(impersonate_version=browser_versions[current_browser_version_index])

    for browser_retry in range(browser_switch_retries + 1):
        data_fetched = False  # Reset data_fetched to False at the beginning of each browser_retry
        with requests.Session() as s:
            # phase 1: token
            for retry in range(max_retries):
                time.sleep(2)
                token_payload = build_payload(keywords)
                url = 'https://trends.google.com/trends/api/explore'
                params = urllib.parse.urlencode(token_payload)
                full_url = f"{url}?{params}"
                response = s.get(full_url, impersonate=browser_versions[current_browser_version_index], cookies=cookies)
                if response.status_code == 200:
                    content = response.text[4:]
                    try:
                        data = json.loads(content)
                        widgets = data['widgets']
                        tokens = {}
                        request = {}
                        for widget in widgets:
                            if widget['id'] == 'TIMESERIES':
                                tokens['timeseries'] = widget['token']
                                request['timeseries'] = widget['request']
                        break  # Break out of the retry loop as we got the token
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON while fetching token, retrying {retry + 1}/{max_retries}")
                else:
                    print(f"Error {response.status_code} while fetching token, retrying {retry + 1}/{max_retries}")
            else:
                print(f"Exceeded maximum retry attempts ({max_retries}) while fetching token. Exiting...")
                return None

            # phase 2: trends data
            for retry in range(max_retries):
                time.sleep(5)
                req_string = json.dumps(request['timeseries'], separators=(',', ':'))
                encoded_req = urllib.parse.quote(req_string, safe=':,+')
                url = f"https://trends.google.com/trends/api/widgetdata/multiline?hl={hl}&tz=0&req={encoded_req}&token={tokens['timeseries']}&tz=0"
                response = s.get(url, impersonate=browser_versions[current_browser_version_index], cookies=cookies)
                if response.status_code == 200:
                    content = response.text[5:]
                    try:
                        raw_data = json.loads(content)
                        # Convert raw data
                        trend_data = convert_to_desired_format(keywords,raw_data)
                        data_fetched = True  # Set data_fetched to True as we have successfully fetched the trend data
                        return trend_data
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON while fetching trends data, retrying {retry + 1}/{max_retries}")
                else:
                    print(f"Error {response.status_code} while fetching trends data, retrying {retry + 1}/{max_retries}")
            else:
                print(f"Exceeded maximum retry attempts ({max_retries}) while fetching trends data.")

        # change browser
        if not data_fetched and browser_retry < browser_switch_retries:
            time.sleep(5)
            current_browser_version_index = (current_browser_version_index + 1) % len(browser_versions)
            print(f"Switching browser version to {browser_versions[current_browser_version_index]} and retrying...")

    print(f"Exceeded maximum browser switch attempts ({browser_switch_retries}). Exiting...")
    return None

def save_to_db(df,table,keyword,conn):
    from sqlalchemy.exc import SQLAlchemyError
    query ="DELETE FROM dbo.{} WHERE nama_perusahaan='{}'".format(table,keyword)
    try:
        r_set=conn.execute(text(query))
    except SQLAlchemyError as e:
        print(e._message)
    else:
        print("No of Records deleted : ",r_set.rowcount)

    df.to_sql('trends',conn,if_exists='append', index=False)
    conn.commit()

def get_trend_google_trend(keywords):
    import plotly
    import plotly.express as px
    trends_data = fetch_trends_data(keywords)
    fig = px.line(trends_data, x="periode", y='trend_value',color='nama_perusahaan',title='Minat Seiring waktu')
    graphJSON_overtime = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return trends_data,graphJSON_overtime

def get_trend(keywords):
    import plotly.express as px
    nama_perusahaan=""
    for keyword in keywords:
        nama_perusahaan+="'{}',".format(keyword)
    nama_perusahaan=nama_perusahaan[:-1]
    conn = connect_sql_server()
    if conn:
        query="SELECT * From dbo.trends where nama_perusahaan in ({}) order by periode asc"
        df_overtime=pd.read_sql(query,conn)
        conn.close()
        fig = px.line(df_overtime, x="periode", y='trend_value',color='nama_perusahaan',title='Minat Seiring waktu')
        graphJSON_overtime = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    
    return df_overtime,graphJSON_overtime
    

if __name__=="__main__":
    conn = connect_sql_server()
    if conn:
        query="SELECT DISTINCT [NAMA PERUSAHAAN] as NAMA_PERUSAHAAN FROM Direktori"
        df=pd.read_sql(query,conn)    
        
        keywords = df['NAMA_PERUSAHAAN'].values
        #print(keywords)
        for keyword in keywords:
            #print(keyword)
            trends_data = fetch_trends_data([keyword])
            #print(trends_data)
            if not None in trends_data:
                save_to_db(trends_data,'trends', keyword,conn)
        conn.close()
  
