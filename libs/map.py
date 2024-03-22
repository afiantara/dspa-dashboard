import requests
import pandas as pd
import folium
import geopandas as gpd

def prepare():
    # Import GeoJSON Data
    file_geo = './libs/gadm36_IDN_1.json'
    df_geo = gpd.read_file(file_geo)
    #print(df_geo.head())
    return df_geo

def showmap(df,keywords):
    df_geo = prepare()
    df['geoCode'] = df['geoCode'].replace({"ID-": "ID."},regex=True)
    df_merged = df_geo.merge(df, how='inner', left_on='HASC_1', right_on='geoCode')

    map_indo = folium.Map(location=[-2.49607,117.89587], zoom_start=5)

    folium.Choropleth(
        geo_data=df_merged,
        data=df_merged,
        columns=df.columns,
        key_on='feature.properties.geoCode',
        fill_color='YlOrRd',
        fill_opacity=1,
        line_opacity=0.2,
        smooth_factor=0,
        Highlight= True,
        line_color = '#0000',
        show=True,
        overlay=True
    ).add_to(map_indo)
    # Add a layer controller
    #folium.LayerControl(collapsed=False).add_to(map_indo)
    map_indo.get_root().render()
    iframe = map_indo.get_root()._repr_html_()
    return iframe


if __name__=="__main__":
    prepare()