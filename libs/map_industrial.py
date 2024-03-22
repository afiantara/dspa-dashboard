import requests
import sqlite3
import pandas as pd
import geopandas as gpd
import folium

db_name = 'datasets/Data_Kantor_Selain_KP.db'

def prepare_geo():
    # Import GeoJSON Data
    file_geo = './libs/gadm36_IDN_1.json'
    df_geo = gpd.read_file(file_geo)
    #print(df_geo.head())
    return df_geo

def get_dist_by_province():
    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect(db_name)
    query='select ProvinceDesc as Province,count(*)  as Jumlah from  Data_Kantor_Selain_KP  where report_date =(select  max(report_date) from Data_Kantor_Selain_KP)  group by ProvinceDesc'
    df=pd.read_sql_query(query, con)
    con.close()
    return df

def do_map():
    df_geo =prepare_geo()
    df_geo['NAME_1'] =df_geo['NAME_1'].replace(['Jakarta Raya'],'DKI Jakarta') 
    df_geo['NAME_1'] =df_geo['NAME_1'].replace(['Yogyakarta'],'Daerah Istimewa Yogyakarta')
    df_data=get_dist_by_province()
    #print(df_data)
    #print(df_geo)
    df_merged = df_geo.merge(df_data, how='inner', left_on='NAME_1', right_on='Province')
    map_indo = folium.Map(location=[-2.49607,117.89587], zoom_start=4)
    
    folium.Choropleth(
        geo_data=df_merged,
        data=df_merged,
        columns=df_data.columns,
        key_on='feature.properties.Province',
        fill_color='YlOrRd',
        fill_opacity=1,
        line_opacity=0.2,
        smooth_factor=0,
        Highlight= True,
        line_color = '#0000',
        show=True,
        overlay=True
    ).add_to(map_indo)
    map_indo.get_root().render()
    iframe = map_indo.get_root()._repr_html_()
    return iframe

if __name__=="__main__":
    do_map()
