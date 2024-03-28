import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

db_kinerja ='./datasets/KINERJA.db'

def get_periode(df):
     date = pd.to_datetime(df['REPORT_DATE'], errors='coerce')
     year=date.dt.year.unique()
     return year

def label_point(df, ax):
    #a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in df.iterrows():
        ax.text(point['NAMA_PERUSAHAAN'], point['RBC'], str(point['REPORT_DATE'] + '\n' + point['NAMA_PERUSAHAAN']))

def analisisInvestasi():
    columns=[
        'REPORT_DATE',
        'NAMA_PERUSAHAAN',
        'DEPOSITO',
        'SAHAM',
        'OBLIGASI_MTN',
        'SB_RI',
        'SB_NONRI',
        'SB_JAMINRI',
        'SB_JAMINMULTINASIONAL',
        'REKSADANA',
        'KIK_EBA',
        'REAL_ESTATE',
        'PENYERTAAN_LNGSG',
        'TANAH_BANGUNAN',
        'PIUTAN_PEMBIAYAAN_BANK',
        'EXECUTING',
        'EMAS',
        'PINJAMAN_HAK_TANGGUNG',
        'PINJAMAN_POLIS',
        'INVESTASI_LAIN',
        'JUMLAH_INVESTASI',
        'JUMLAH_INVESTASI_PREV',
        'RATA_RATA_INVESTASI',
        'SECTOR'
    ]
    conn = create_connection('./KINERJA.db')
    query="SELECT REPORT_DATE,NAMA_PERUSAHAAN,[INVESTASI_DEPOSITO_BERJANGKA_DAN_SERTIFIKAT_DEPOSITO],\
        [INVESTASI_SAHAM],[INVESTASI_OBLIGASI_MTN_DAN_SUKUK],[INVESTASI_SURAT_BERHARGA_YG_DITERBITKAN_ATAU_DIJAMIN_OLEH_NEGARA_RI],\
        [INVESTASI_SURAT_BERHARGA_YG_DITERBITKAN_ATAU_DIJAMIN_OLEH_SELAIN_NEGARA_RI],[INVESTASI_SURAT_BERHARGA_YG_DITERBITKAN_ATAU_DIJAMIN_OLEH_BI],\
        [INVESTASI_SURAT_BERHARGA_YG_DITERBITKAN_OLEH_LEMBAGA_MULTINASIONAL],[INVESTASI_UNIT_PENYERTAAN_REKSADANA],\
        [INVESTASI_KONTRAK_INVESTASI_KOLEKTIF_EFEK_BERAGUN_ASET_(KIK_EBA)],[INVESTASI_DANA_INVESTASI_REAL_ESTAT],[INVESTASI_PENYERTAAN_LANGSUNG],\
        [INVESTASI_BANGUNAN_DENGAN_HAK_STRATA_SATU_ATAU_TANAH_DG_BANGUNAN_UNTUK_INVESTASI],[INVESTASI_PEMBELIAN_PIUTANG_UNTUK_PERUSAHAAN_PEMBIAYAAN_DAN/ATAU_BANK],\
        [INVESTASI_PEMBIAYAAN_MELALUI_KERJASAMA_DG_PIHAK_LAIN_(EXECUTING)],[INVESTASI_EMAS_MURNI],\
        [INVESTASI_PINJAMAN_YANG_DIJAMIN_DENGAN_HAK_TANGGUNGAN_(PINJAMAN_HIPOTIK)], NULL AS INVESTASI_PINJAMAN_POLIS, [INVESTASI_INVESTASI_LAIN],\
        [INVESTASI_JUMLAH_INVESTASI],[INVESTASI_JUMLAH_INVESTASI_PREV],[INVESTASI_RATA-RATA_INVESTASI],\
        'non-life' as sector from ASURANSI_UMUM order by REPORT_DATE"
    dfG = pd.read_sql_query( query, conn)
    print(dfG)
    dfG.columns=columns

    print(dfG)

    query="SELECT REPORT_DATE,NAMA_PERUSAHAAN,[INVESTASI_DEPOSITO_BERJANGKA_DAN_DEPOSITO_BERJANGKA],\
        [INVESTASI_SAHAM],[INVESTASI_OBLIGASI_DAN_MTN],[INVESTASI_SURAT_BERHARGA_YANG_DITERBITKAN_OLEH_NEGARA_RI],\
        [INVESTASI_SURAT_BERHARGA_YANG_DITERBITKAN_OLEH_NEGARA_SELAIN_NEGARA_RI],[INVESTASI_SURAT_BERHARGA_YANG_DITERBITKAN_ATAU_DIJAMIN_OLEH_BI],\
        [INVESTASI_SURAT_BERHARGA_YANG_DITERBITKAN_OLEH_LEMBAGA_MULTINASIONAL],[INVESTASI_UNIT_PENYERTAAN_REKSADANA],\
        [INVESTASI_KONTRAK_INVESTASI_KOLEKTIF_EFEK_BERAGUN_ASET_(KIK_EBA)],[INVESTASI_DANA_INVESTASI_REAL_ESTAT],[INVESTASI_PENYERTAAN_LANGSUNG],\
        [BUKAN_INVESTASI_BANGUNAN_DENGAN_HAK_STRATA_ATAU_TANAH_DENGAN_BANGUNAN_UNTUK_DIPAKAI_SENDIRI],[INVESTASI_PEMBELIAN_PIUTANG_UNTUK_PERUSAHAAN_PEMBIAYAAN_DAN/_ATAU_BANK],\
        [INVESTASI_PEMBIAYAAN_MELALUI_KERJASAMA_DG_PIHAK_LAIN_(EXECUTING)],[INVESTASI_EMAS_MURNI],\
        [INVESTASI_PINJAMAN_YANG_DIJAMIN_DENGAN_HAK_TANGGUNGAN],[INVESTASI_PINJAMAN_POLIS],[INVESTASI_INVESTASI_LAIN],\
        [INVESTASI_JUMLAH_INVESTASI],[INVESTASI_JUMLAH_INVESTASI_PREV],[INVESTASI_RATA-RATA_INVESTASI],\
        'life' as sector from ASURANSI_JIWA order by REPORT_DATE"
    print(query)
    dfL = pd.read_sql_query( query, conn)
    dfL.columns=columns
    df = pd.concat([dfG,dfL],axis=0)
    #df=convertStrToFloat(df,columns)
    print(df)
    from ydata_profiling import ProfileReport
    profile = ProfileReport(df, title='Pandas Profiling Report', html={'style':{'full_width':False}})
    profile.to_file(output_file="REPORT.html")
    #plotPerColumnDistribution(df,30,5)
    #plotCorrelationMatrix(df,10)
    #plotCorrelationMatrix(df1, 21)
    print(profile)

def PlotAllRasio(df,year=None):
    import numpy as np
    df=cleansing(df)
    df['date'] = pd.to_datetime(df['REPORT_DATE'], errors='coerce')
    df['yr']=df['date'].dt.year
    grouped= df.groupby(['yr','sector'])
    average_df = grouped.mean()
    average_df=average_df.reset_index()
    if year:
        average_df=average_df.query("yr>={}".format(year))
    else:
        average_df=average_df.query("yr>2017")
    return average_df

def ShowAllRasio(df):
    df=cleansing(df)
    df['date'] = pd.to_datetime(df['REPORT_DATE'], errors='coerce')
    df['yr']=df['date'].dt.year
    grouped = df.groupby(['yr','sector'])
    average_df = grouped.mean()    
    print(average_df)
    average_df=average_df.reset_index()
    fig, axes = plt.subplots(3, 2, figsize=(18, 10))

    sns.catplot(kind='bar', data=average_df, x='yr', y='RBC', hue='sector', 
            order=sorted(average_df.yr.unique()), col_order=sorted(average_df.sector.unique()))

    #sns.barplot(ax=axes[0, 0], data=average_df, x='yr',  y='RBC')
    #sns.barplot(ax=axes[0, 1], data=average_df, x='yr', y='RKI',hue='sector')
    #sns.barplot(ax=axes[1, 0], data=average_df, x='yr', y='RLiq',hue='sector')
    #sns.barplot(ax=axes[1, 1], data=average_df, x='yr', y='RPHI',hue='sector')
    #sns.barplot(ax=axes[2, 0], data=average_df, x='yr', y='RBPN',hue='sector')

    fig.suptitle('Analisis Kinerja Industri Asuransi (Rasio)')
    plt.subplots_adjust(hspace=0.435,wspace=0.370)
    plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
    plt.show()

def PlotRBC(df):
    df=cleansing(df)
    sorted_df = df.sort_values(by=['REPORT_DATE'], ascending=True)
    sorted_df=sorted_df.query('RBC <1000')
    return sorted_df

def RBC(df):
    df=cleansing(df)
    df=df.query('RBC <10000')
    #ax=sns.scatterplot(data=df,x='NAMA_PERUSAHAAN',y='RBC',hue='sector')
    ax=sns.scatterplot(data=df,x='NAMA_PERUSAHAAN',y='RBC',hue='sector')
    ax.set(xticklabels=[])
    #label_point(df, ax) 
    [ax.axhline(y=i, linestyle='--') for i in [120]]
    plt.suptitle('Distribusi RBC Perusahaan Asuransi')
    plt.show()

def PlotRKI(df):
    df=cleansing(df)
    sorted_df = df.sort_values(by=['REPORT_DATE'], ascending=True)
    sorted_df=sorted_df.query('RKI <1000')
    return sorted_df

def RKI(df):
    df=cleansing(df)
    df=df.query('RBC <10000')
    #ax=sns.scatterplot(data=df,x='NAMA_PERUSAHAAN',y='RBC',hue='sector')
    ax=sns.scatterplot(data=df,x='NAMA_PERUSAHAAN',y='RKI',hue='sector')
    ax.set(xticklabels=[])
    #label_point(df, ax) 
    [ax.axhline(y=i, linestyle='--') for i in [120]]
    plt.suptitle('Distribusi RKI Perusahaan Asuransi')
    plt.show()

def cleansing(df):
    df=df.dropna()
    df["RBC"] = [float(str(i).replace(",", "")) for i in df["RBC"]]
    df["RKI"] = [float(str(i).replace(",", "")) for i in df["RKI"]]
    df["RLiq"] = [float(str(i).replace(",", "")) for i in df["RLiq"]]
    df["RPHI"] = [float(str(i).replace(",", "")) for i in df["RPHI"]]
    df["RBPN"] = [float(str(i).replace(",", "")) for i in df["RBPN"]]
    return df


def Top10(df,sector,ascending=False):
    df =cleansing(df)
    df = df[df['sector']==sector]
    dfmax=df['REPORT_DATE'].agg(['max'])
    df = df[df['REPORT_DATE']==dfmax['max']]
    dfRBC=df.sort_values(by=['RBC'],
               ascending=[ascending])
    
    dfRKI=df.sort_values(by=['RKI'],
               ascending=[ascending])

    dfRBC=dfRBC.head(10)
    dfRKI=dfRKI.head(10)
    yr= dfmax['max'].split('-')[0]
    return dfRBC,dfRKI,yr


def Top10RBC(df,sector):
    df =cleansing(df)
    df = df[df['sector']==sector]

    dfmax=df['REPORT_DATE'].agg(['max'])

    df = df[df['REPORT_DATE']==dfmax['max']]
    df=df.sort_values(by=['RBC'],
               ascending=[False])
    dfchart=df.head(10)
    sns.barplot(x='RBC', y='NAMA_PERUSAHAAN', orient='h',data=dfchart)
    if sector=='life':
        plt.suptitle('Top 10 Asuransi Jiwa RBC - Tahun 2022')
    else:
        plt.suptitle('Top 10 Asuransi Umum RBC - Tahun 2022')    
    print(df.head(10))
    plt.show()

def Top10RKI(df,sector):
    df =cleansing(df)
    df = df[df['sector']==sector]

    dfmax=df['REPORT_DATE'].agg(['max'])

    df = df[df['REPORT_DATE']==dfmax['max']]
    df=df.sort_values(by=['RKI'],
               ascending=[False])
    dfchart=df.head(10)
    sns.barplot(x='RKI', y='NAMA_PERUSAHAAN', orient='h',data=dfchart)
    if sector=='life':
        plt.suptitle('Top 10 Asuransi Jiwa RKI - Tahun 2022')
    else:
        plt.suptitle('Top 10 Asuransi Umum RKI - Tahun 2022')    
    print(df.head(10))
    plt.show()

def PlotInsolvenRBC(df):
    df =cleansing(df)
    df=df.query('RBC <120')
    sorted_df = df.sort_values(by=['REPORT_DATE'], ascending=True)
    return sorted_df

def PlotInsolvenRKI(df):
    df =cleansing(df)
    df=df.query('RKI <100')
    sorted_df = df.sort_values(by=['REPORT_DATE'], ascending=True)
    return sorted_df


def InsolvenRBC(df,sector):
    df =cleansing(df)
    df=df.query('RBC <120')
    df = df[df['sector']==sector]
    ax=sns.scatterplot(data=df,x='NAMA_PERUSAHAAN',y='RBC',hue='sector')
    ax.set(xticklabels=[])
    label_point(df, ax) 
    if sector=='life':
        plt.suptitle('Asuransi Jiwa yang pernah RBC < 120')
    else:
        plt.suptitle('Asuransi Umum yang pernah RBC < 120')    

    print(df.head(10))
    plt.show()

def Lose10RBC(df,sector):
    df =cleansing(df)
    
    #df = df.query('RBC <120')
    
    df = df[df['sector']==sector]
    df = df[df['REPORT_DATE']=='2022-12-31']
    df=df.sort_values(by=['RBC'],
               ascending=[True])
    dfchart=df.head(10)
    sns.barplot(x='RBC', y='NAMA_PERUSAHAAN', orient='h',data=dfchart)
    if sector=='life':
        plt.suptitle('Loser 10 Asuransi Jiwa RBC - Tahun 2022')
    else:
        plt.suptitle('Loser 10 Asuransi Umum RBC - Tahun 2022')    
    print(df.head(10))
    plt.show()


def Individual_RBC(df,names):
    kwstr = '|'.join(names)
    df  = df[df['NAMA_PERUSAHAAN'].str.contains(kwstr)]
    ax=sns.scatterplot(data=df,x='REPORT_DATE',y='RBC',hue='NAMA_PERUSAHAAN')
    plt.axhline(y=120)
    plt.show()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except :
        print('error database')
    return conn

def get_ratios():
    conn1 = create_connection(db_kinerja)
    df1 = pd.read_sql_query("select REPORT_DATE,NAMA_PERUSAHAAN,[MODAL_MINIMUM_BERBASIS_RISIKO_(MMBR)_RASIO_PENCAPAIAN_(%)_RBC] AS RBC,[INFORMASI_LAIN_RASIO_KECUKUPAN_INVESTASI_(RASIO_INVESTASI_(SAP)_TERHADAP_CAD.TEKNIS_&_UTANG_KLAIM)_(%)] AS RKI,[INFORMASI_LAIN_RASIO_LIKUIDITAS_(%)] AS RLiq,[INFORMASI_LAIN_RASIO_PERIMBANGAN_HASIL_INVESTASI_DENGAN_PENDAPATAN_PREMI_NETO_(%)] AS RPHI,[INFORMASI_LAIN_RASIO_BEBAN_(KLAIM,_USAHA_DAN_KOMISI)_TERHADAP_PENDAPATAN_PREMI_NETO_(%)] AS RBPN,'life' AS sector from ASURANSI_JIWA order by REPORT_DATE", conn1)
    df2 = pd.read_sql_query("select REPORT_DATE,NAMA_PERUSAHAAN,[RASIO_PENCAPAIAN_(%)_RBC] AS RBC,[RASIO_KECUKUPAN_INVESTASI_(%)] as RKI,[RASIO_LIKUIDITAS_(%)] AS RLiq,[RASIO_PERIMBANGAN_HASIL_INVESTASI_DENGAN_PENDAPATAN_PREMI_NETO_(%)] AS RPHI,[RASIO_BEBAN_(KLAIM,_USAHA_DAN_KOMISI)_TERHADAP_PEN-_DAPATAN_PREMI_NETO_(%)] as RBPN,'non-life' AS sector from ASURANSI_UMUM order by REPORT_DATE", conn1)
    df3 = pd.concat([df1,df2],axis=0)
    return df3

def get_companies(isJiwa=True):
    conn1 = create_connection(db_kinerja)
    if isJiwa:
        query="SELECT distinct TRIM(NAMA_PERUSAHAAN) AS NAMA_PERUSAHAAN FROM ASURANSI_JIWA WHERE NAMA_PERUSAHAAN NOT in ('TOTAL','RATA-RATA') AND NAMA_PERUSAHAAN NOT LIKE '-%'"
    else:
        query="SELECT distinct TRIM(NAMA_PERUSAHAAN) AS NAMA_PERUSAHAAN FROM ASURANSI_UMUM WHERE NAMA_PERUSAHAAN NOT in ('TOTAL','RATA-RATA') AND NAMA_PERUSAHAAN NOT LIKE '-%'"
    df = pd.read_sql_query(query,conn1)
    return df['NAMA_PERUSAHAAN'].values

def get_accounts(isJiwa=True):
    conn1 = create_connection(db_kinerja)
    if isJiwa:
        query='SELECT * FROM ASURANSI_JIWA LIMIT 1'
    else:
        query='SELECT * FROM ASURANSI_UMUM LIMIT 1'
    df = pd.read_sql_query(query,conn1)
    accounts = df.columns
    accounts=accounts[3:-1]
    return accounts

def split_strip(datas,addon=0):
    strdata=''
    for data in datas:
        if addon==0:
            strdata+="[{}],".format(data.strip())
        elif addon==1:
            strdata+="'{}',".format(data.strip())
        else:
            strdata+="{},".format(data.strip())
    return strdata[:-1]

def get_data_by_account_jiwa(company,account):
    conn1 = create_connection(db_kinerja)
    query1="SELECT REPORT_DATE,NAMA_PERUSAHAAN,{} FROM ASURANSI_JIWA WHERE TRIM(NAMA_PERUSAHAAN) in ({}) order by NAMA_PERUSAHAAN,REPORT_DATE asc".format(account,company)
    print(query1)
    df1 = pd.read_sql_query(query1,conn1)
    return df1

def get_data_by_account_umum(company,account):
    conn1 = create_connection(db_kinerja)
    query1="SELECT REPORT_DATE,NAMA_PERUSAHAAN,{} FROM ASURANSI_UMUM WHERE TRIM(NAMA_PERUSAHAAN) in ({}) order by NAMA_PERUSAHAAN,REPORT_DATE asc".format(account,company)
    df1 = pd.read_sql_query(query1,conn1)
    return df1
    

def get_datas():
    conn1 = create_connection(db_kinerja)
    query1='SELECT * FROM ASURANSI_JIWA order by REPORT_DATE asc'
    query2='SELECT * FROM ASURANSI_UMUM order by REPORT_DATE asc'
    df1 = pd.read_sql_query(query1,conn1)
    df2 = pd.read_sql_query(query2,conn1)
    companies_jiwa = df1['NAMA_PERUSAHAAN']
    companies_umum = df2['NAMA_PERUSAHAAN']
    companies = pd.concat([companies_jiwa,companies_umum],axis=0)
    
    companies = companies.unique()
    companies_jiwa=companies_jiwa.unique()
    companies_umum=companies_umum.unique()

    #get account..
    accounts_jiwa = df1.columns
    accounts_umum = df2.columns
    accounts_jiwa=accounts_jiwa[3:-1]
    accounts_umum=accounts_umum[3:-1]

    return [accounts_jiwa,accounts_umum, companies_jiwa,companies_umum,companies,df1,df2]

if __name__=="__main__":
    '''
    conn1 = create_connection(db_kinerja)
    df1 = pd.read_sql_query("select REPORT_DATE,NAMA_PERUSAHAAN,[MODAL_MINIMUM_BERBASIS_RISIKO_(MMBR)_RASIO_PENCAPAIAN_(%)_RBC] AS RBC,[INFORMASI_LAIN_RASIO_KECUKUPAN_INVESTASI_(RASIO_INVESTASI_(SAP)_TERHADAP_CAD.TEKNIS_&_UTANG_KLAIM)_(%)] AS RKI,[INFORMASI_LAIN_RASIO_LIKUIDITAS_(%)] AS RLiq,[INFORMASI_LAIN_RASIO_PERIMBANGAN_HASIL_INVESTASI_DENGAN_PENDAPATAN_PREMI_NETO_(%)] AS RPHI,[INFORMASI_LAIN_RASIO_BEBAN_(KLAIM,_USAHA_DAN_KOMISI)_TERHADAP_PENDAPATAN_PREMI_NETO_(%)] AS RBPN,'life' AS sector from ASURANSI_JIWA order by REPORT_DATE", conn1)
    df2 = pd.read_sql_query("select REPORT_DATE,NAMA_PERUSAHAAN,[RASIO_PENCAPAIAN_(%)_RBC] AS RBC,[RASIO_KECUKUPAN_INVESTASI_(%)] as RKI,[RASIO_LIKUIDITAS_(%)] AS RLiq,[RASIO_PERIMBANGAN_HASIL_INVESTASI_DENGAN_PENDAPATAN_PREMI_NETO_(%)] AS RPHI,[RASIO_BEBAN_(KLAIM,_USAHA_DAN_KOMISI)_TERHADAP_PEN-_DAPATAN_PREMI_NETO_(%)] as RBPN,'non-life' AS sector from ASURANSI_UMUM order by REPORT_DATE", conn1)
    df3 = pd.concat([df1,df2],axis=0)
    '''
    #company = get_companies()
    #print(company.values)
    company ="'BNI LIFE INSURANCE'"
    accounts = '[JUMLAH_KEKAYAAN],[INVESTASI_JUMLAH_INVESTASI]'
    account_chart=['JUMLAH_KEKAYAAN','INVESTASI_JUMLAH_INVESTASI']
    df = get_data_by_account_jiwa(company,accounts)
    print(df)
    import plotly
    import plotly.express as px

    fig = px.line(df, x='REPORT_DATE', y=account_chart, title='Compare',color='NAMA_PERUSAHAAN')
    fig.update_layout(showlegend=False)
    fig.show()

    #print(companies)
    #RBC(df3)
    #Top10RBC(df3,'life')
    #Top10RBC(df3,'non-life')
    #Top10Life(df3,'life')
    #Lose10RBC(df3,'life')
    #InsolvenRBC(df3,'life')
    #Individual_RBC(df3,['HEKSA EKA','JIWA TUGU','PASARAYA'])
    #ShowAllRasio(df3)
    #analisisInvestasi()