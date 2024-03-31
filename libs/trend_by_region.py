import json
import urllib.parse
from curl_cffi import requests
import time
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,text

BASE_TRENDS_URL = 'https://trends.google.com/trends'
INTEREST_BY_REGION_URL = f'{BASE_TRENDS_URL}/api/widgetdata/comparedgeo'

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
    cols=['geoCode','geoName'] + keywords
    datas=[]
    for entry in raw_data['default']['geoMapData']:
        datas.append([entry['geoCode']]+[entry['geoName']]+entry['value'])
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
                            if widget['id']=='GEO_MAP':
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
                #print(request['timeseries'])
                req_string = json.dumps(request['timeseries'], separators=(',', ':'))
                encoded_req = urllib.parse.quote(req_string, safe=':,+')
                #url = f"https://trends.google.com/trends/api/widgetdata/multiline?hl={hl}&tz=0&req={encoded_req}&token={tokens['timeseries']}&tz=0"
                url =INTEREST_BY_REGION_URL+f"?hl={hl}&tz=0&req={encoded_req}&token={tokens['timeseries']}&tz=0"
                #print(url)
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

def do_mapPlotly(df_data,keywords):
    import plotly.express as px
    import geopandas as gpd
    loc_json = './libs/indonesia.geojson'
    ina= gpd.read_file(loc_json)
    ina['state'] =ina['state'].replace(['Jakarta Raya'],'Daerah Khusus Ibukota Jakarta') 
    ina['state'] =ina['state'].replace(['Yogyakarta'],'Daerah Istimewa Yogyakarta')
    ina['state'] =ina['state'].replace(['Bangka-Belitung'],'Kepulauan Bangka Belitung')
    #drop kalimantan utara dan papua barat
    df_data = df_data.drop(df_data[df_data['geoName'] == 'Kalimantan Utara'].index)
    df_data = df_data.drop(df_data[df_data['geoName'] == 'Papua Barat'].index)
    
    df_merged = ina.merge(df_data, how='inner', left_on='state', right_on='geoName')
    fig = px.choropleth(
        df_merged, geojson=df_merged,
        locations="geoName", featureidkey="properties.geoName",
        color=keywords,
        color_continuous_scale = px.colors.sequential.Plasma,
        range_color=[0, 100])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def do_mapPlotly_01(df_data,keywords):
    import plotly.express as px
    import geopandas as gpd
    import pandas as pd
    loc_json = './libs/indonesia.geojson'
    ina= gpd.read_file(loc_json)
    ina['state'] =ina['state'].replace(['Jakarta Raya'],'Daerah Khusus Ibukota Jakarta') 
    ina['state'] =ina['state'].replace(['Yogyakarta'],'Daerah Istimewa Yogyakarta')
    ina['state'] =ina['state'].replace(['Bangka-Belitung'],'Kepulauan Bangka Belitung')
    #drop kalimantan utara dan papua barat
    df_data = df_data.drop(df_data[df_data['geoName'] == 'Kalimantan Utara'].index)
    df_data = df_data.drop(df_data[df_data['geoName'] == 'Papua Barat'].index)
    new_df = pd.DataFrame(df_data[keywords],columns=keywords)
    df_data['winner']= new_df.idxmax(axis=1)
    df_merged = ina.merge(df_data, how='inner', left_on='state', right_on='geoName')
    fig = px.choropleth(
        df_merged, geojson=df_merged,
        locations="geoName", featureidkey="properties.geoName",
        color='winner',
        color_continuous_scale = px.colors.sequential.Plasma,
        range_color=[0, 100],
        hover_data=keywords)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def get_trend_by_region_google_trend(keywords):
    import plotly
    data_geo = fetch_trends_data(keywords)
    fig = do_mapPlotly_01(data_geo,keywords)
    graphJSON_map = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return data_geo,graphJSON_map

def get_trend_by_region(keywords):
    #Mengambil data geo map
    import plotly
    import pandas as pd
    conn=connect_sql_server()
    for keyword in keywords:
        if keyword=='': continue
        geo=is_exist(keyword,conn)
        if geo['JML'][0]==0:
            data_geo = fetch_trends_data([keyword])
            df =pd.DataFrame(columns=['NAMA_PERUSAHAAN','GEO_NAME','GEO_VALUE'])
            df['GEO_NAME']          = data_geo['geoName']
            df['GEO_VALUE']         = data_geo[keyword]
            df['NAMA_PERUSAHAAN']   = keyword
            save_to_db(df,'trends_geo',keyword,conn)
    list_geo=[]
    for keyword in keywords:
        data_geo = get_trend_go_db(keyword,conn)
        df =pd.DataFrame(columns=['geoName',keyword])
        df['geoName'] = data_geo['GEO_NAME']
        df[keyword]   = data_geo['GEO_VALUE']
        fig = do_mapPlotly(df,keyword)
        graphJSON_map = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
        list_geo.append(graphJSON_map)
    
    graphJSON_bar=show_bar_graph(keywords,conn)
    
    conn.close()
    
    return list_geo,graphJSON_bar

def get_trend_go_db(keyword,conn):
    import pandas as pd
    df = pd.DataFrame()
    if conn:
        query=f"SELECT * From dbo.trends_geo where NAMA_PERUSAHAAN='{keyword}'"
        df=pd.read_sql(query,conn)
    return df

def is_exist(keyword,conn):
    import pandas as pd
    df = pd.DataFrame()
    if conn:
        query=f"SELECT COUNT(*)  as JML From dbo.trends_geo where NAMA_PERUSAHAAN='{keyword}'"
        df=pd.read_sql(query,conn)
    return df


def connect_sql_server():
    load_dotenv('./.env')
    SERVER_DB = os.getenv('SERVER')
    DB=os.getenv("DATABASE")
    USER = os.getenv("USERNAME")
    PWD = os.getenv("PASSWORD")
    
    connstring="DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection=no".format(SERVER_DB,DB,USER,PWD)
    print(connstring)
    
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(connstring))
    conn = engine.connect()
    return conn

def save_to_db(df,table,keyword,conn):
    from sqlalchemy.exc import SQLAlchemyError
    query ="DELETE FROM dbo.{} WHERE NAMA_PERUSAHAAN='{}'".format(table,keyword)
    try:
        r_set=conn.execute(text(query))
    except SQLAlchemyError as e:
        print(e._message)
    else:
        print("No of Records deleted : ",r_set.rowcount)

    df.to_sql('trends_geo',conn,if_exists='append', index=False)
    conn.commit()

def show_bar_graph(keywords,conn):
    import pandas as pd
    import plotly
    import plotly.express as px
    nama =''
    for keyword in keywords:
        nama+="'{}',".format(keyword)
    nama = nama[:-1]
    if conn:
        query=f"SELECT * From dbo.trends_geo where NAMA_PERUSAHAAN in ({nama})"
        df=pd.read_sql(query,conn)
        fig = px.bar(df, x="GEO_VALUE", y='GEO_NAME', title='PERBANDINGAN MINAT ANTAR WILAYAR',color='NAMA_PERUSAHAAN',orientation='h')
        fig.update_layout(showlegend=False)
        graphJSON_bar = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_bar
    
if __name__=="__main__":
    '''
    keywords=['PT AIA FINANCIAL']
    conn = connect_sql_server()
    if conn:
        df = get_trend_by_region(keywords)
    '''    
    #trends_data = fetch_trends_data(keywords)
    #print(trends_data)
  
