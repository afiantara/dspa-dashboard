import os
import pyodbc
from  sqlalchemy import create_engine
import pandas as pd
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


def get_companies():
    conn = connect_sql_server()
    if conn:
        query="SELECT [Nama Perusahaan] as NAMA_PERUSAHAAN,sektor From dbo.Direktori where report_date=(select max(report_date) from dbo.Direktori)"
        df=pd.read_sql(query,conn)
        conn.close()
    return df    

def get_compare_trend(aj,au):
    conn = connect_sql_server()
    if conn:
        if len(aj)>0 and len(au)>0:
            query="SELECT periode,nama_perusahaan,trend_value From dbo.trends where nama_perusahaan in ({},{}) order by periode asc,nama_perusahaan".format(aj,au)
        if len(aj)>0:
            query="SELECT periode,nama_perusahaan,trend_value From dbo.trends where nama_perusahaan in ({}) order by periode asc,nama_perusahaan".format(aj)
        if len(au)>0:
            query="SELECT periode,nama_perusahaan,trend_value From dbo.trends where nama_perusahaan in ({}) order by periode asc,nama_perusahaan".format(au)
        print(query)
        df=pd.read_sql(query,conn)
        conn.close()
    return df
