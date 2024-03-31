from pytrends.request import TrendReq
import pandas as pd
import json
import plotly
import plotly.express as px
import geopandas as gpd
import folium
from map import showmap,prepare
from tools_sqlite import save_to_db,create_connection

#from map import showmap,prepare

def init():
    #Setup and Import Required Libraries
    #pytrends = TrendReq(hl='id-ID', retries=3)   
    pytrends = TrendReq(
        hl="id-ID",
        tz=360,
        timeout=(10, 25),
        retries=2,
        backoff_factor=1,
        requests_args={"verify": False},
    )
    #pytrends = TrendReq(hl='id-ID', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})
    return pytrends  

def get_trend_db(keywords):
    try:
        db_name='./datasets/trends.db'
        conn= create_connection(db_name)
        query="SELECT * from trend WHERE keywords='{}'".format(keywords)
        df = pd.read_sql_query(query,conn)
        return df
    except:
        return pd.DataFrame()
    
    
def get_trend(keywords,timeframe,resolution,pn):
    df_trend = get_trend_db(keywords)
    if df_trend.shape[0]==0:
        pytrends = init()
        kw_list = keywords # list of keywords to get data 
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe)#,geo='ID') 
        #1 Interest over Time
        data_overtime = pytrends.interest_over_time() 
        data_overtime = data_overtime.reset_index() 
        data = data_overtime.copy()
        data['keywords']=keywords
        
        db_name = './datasets/trends.db'
        tbl_name = 'trend'
        save_to_db(db_name,tbl_name,data)    
    
    else:
        data_overtime=df_trend.copy()
    
    fig = px.line(data_overtime, x="date", y=keywords, title='Keyword Web Search Interest Over Time')
    graphJSON_overtime = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    
    return data_overtime,graphJSON_overtime    

def last5yeartrend(keywords):
    pytrends = init()
    kw_list = keywords # list of keywords to get data 
    pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y',geo='ID') 
    #1 Interest over Time
    data = pytrends.interest_over_time() 
    data = data.reset_index() 
    #print(data)
    fig = px.line(data, x="date", y=keywords, title='Keyword Web Search Interest Over Time')
    fig.show() 
    
    #Mengambil data
    data_geo=pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=True)
    #print(data_geo)
    
    header,body_html,script = showmap(data_geo)
    
    data  = pytrends.related_queries()
    for keyword in keywords:
        print(keyword)
        data[keyword]['top'] 
    
    print(f'data_q',keyword,data)
    
    for keyword in keywords:
        keywords = pytrends.suggestions(keyword=keyword)
        df = pd.DataFrame(keywords)
        print(f'data_s',keyword,df)
    
    #Mengambil data trending
    data_search = pytrends.trending_searches(pn='indonesia')
    print(f'data_search:',data_search)
    
    return ''

if __name__=="__main__":
    keywords = ['Jiwasraya','Wanaartha Life']
    #set keyword
    #mengambil data
    
    import urllib3
    http = urllib3.PoolManager()
    url = 'https://trends.google.com/trends/explore?q=Jiwasraya,Wanaartha&date=now%205-y&geo=ID'
    resp = http.request('GET', url)
    print(resp.status)
    
    pytrends = TrendReq()
    pytrends.build_payload(keywords, timeframe='today 5-y')
    result = pytrends.interest_over_time()
    db_name = './datasets/trends.db'
    tbl_name = 'trend'
    save_to_db(db_name,tbl_name,result)  
    #print(result)
    #data_overtime,graphJSON_overtime,data_geo,data_q,data_search = get_trend(keywords,'today 5-y','DMA','indonesia')

    #last5yeartrend(keywords)

