import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

db_insurance_file='./datasets/insurance.db'
db_data_kantor='./datasets/direktori/Data_Kantor_Selain_KP.db'
db_direktori_aj='./datasets/direktori/Asuransi_Jiwa.db'
db_direktori_au='./datasets/direktori/Asuransi_Umum.db'
db_direktori_reas='./datasets/direktori/Reasuransi.db'
db_direktori_aw='./datasets/direktori/Asuransi_Wajib.db'
db_direktori_as='./datasets/direktori/Asuransi_Sosial.db'

def plotRasioIndustri(df):
    df['date'] = pd.to_datetime(df['Periode'], errors='coerce')
    dfChart=df[['date','ROA','ROE','Investment Yield Ratio',
            'Loss Ratio','Expense Ratio',
            'Combined Ratio','Cession Ratio','Retention Ratio',
            'Net Income Ratio','Liquid Ratio','Investment Adequacy Ratio',
            'Premium to Claim Ratio','Premium to Claim and G/A Ratio', 'sector']]
    dfChart=dfChart.dropna()
    return dfChart

def RasioIndustri(df):
    df['date'] = pd.to_datetime(df['Periode'], errors='coerce')
    dfChart=df[['date','ROA','ROE','Investment Yield Ratio',
            'Loss Ratio','Expense Ratio',
            'Combined Ratio','Cession Ratio','Retention Ratio',
            'Net Income Ratio','Liquid Ratio','Investment Adequacy Ratio',
            'Premium to Claim Ratio','Premium to Claim and G/A Ratio', 'sector']]
    dfChart=dfChart.dropna()

    fig, axes = plt.subplots(3, 4, figsize=(18, 10))

    sns.lineplot(ax=axes[0, 0], data=dfChart, x='date', y='ROA',hue='sector')
    sns.lineplot(ax=axes[0, 1], data=dfChart, x='date', y='ROE',hue='sector')
    sns.lineplot(ax=axes[0, 2], data=dfChart, x='date', y='Investment Yield Ratio',hue='sector')
    sns.lineplot(ax=axes[0, 3], data=dfChart, x='date', y='Loss Ratio',hue='sector')
    sns.lineplot(ax=axes[1, 0], data=dfChart, x='date', y='Expense Ratio',hue='sector')
    sns.lineplot(ax=axes[1, 1], data=dfChart, x='date', y='Combined Ratio',hue='sector')
    sns.lineplot(ax=axes[1, 2], data=dfChart, x='date', y='Cession Ratio',hue='sector')
    sns.lineplot(ax=axes[1, 3], data=dfChart, x='date', y='Retention Ratio',hue='sector')
    sns.lineplot(ax=axes[2, 0], data=dfChart, x='date', y='Net Income Ratio',hue='sector')
    sns.lineplot(ax=axes[2, 1], data=dfChart, x='date', y='Liquid Ratio',hue='sector')
    sns.lineplot(ax=axes[2, 2], data=dfChart, x='date', y='Investment Adequacy Ratio',hue='sector')
    sns.lineplot(ax=axes[2, 3], data=dfChart, x='date', y='Premium to Claim Ratio',hue='sector')
    #sns.lineplot(ax=axes[2, 3], data=dfChart, x='date', y='Premium to Claim and G/A Ratio',hue='sector')

    axes[0,0].get_legend().remove()
    axes[0,1].get_legend().remove()
    axes[0,2].get_legend().remove()
    axes[0,3].get_legend().remove()
    axes[1,0].get_legend().remove()
    axes[1,1].get_legend().remove()
    axes[1,2].get_legend().remove()
    axes[1,3].get_legend().remove()
    axes[2,0].get_legend().remove()
    axes[2,1].get_legend().remove()
    axes[2,2].get_legend().remove()
    axes[2,3].get_legend().remove()

    fig.suptitle('Analisis Kinerja Industri Asuransi')
    plt.subplots_adjust(hspace=0.435,wspace=0.370)
    plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
    plt.show()

def plotGrowthIndustry(df):
    df['date'] = pd.to_datetime(df['Periode'], errors='coerce')
    dfChart=df[['date','Growth_Total Assets','Growth_Total Investment','Growth_Investment Yield',
            'Growth_Premium Income','Growth_Total Claims and Benefits',
            'Growth_Total Operating Expenses','Growth_Total Net Premium Income','sector']]
    dfChart=dfChart.dropna()
    return dfChart
    
def GrowthIndustri(df):
    # Create a visualization
    # Some example data to display
    df['date'] = pd.to_datetime(df['Periode'], errors='coerce')
    dfChart=df[['date','Growth_Total Assets','Growth_Total Investment','Growth_Investment Yield',
            'Growth_Premium Income','Growth_Total Claims and Benefits',
            'Growth_Total Operating Expenses','Growth_Total Net Premium Income','sector']]
    
    dfChart=dfChart.dropna()
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Analisis Kinerja Industri Asuransi')

    sns.lineplot(ax=axes[0, 0], data=dfChart, x='date', y='Growth_Total Assets',hue='sector')
    sns.lineplot(ax=axes[0, 1], data=dfChart, x='date', y='Growth_Total Investment',hue='sector')
    sns.lineplot(ax=axes[0, 2], data=dfChart, x='date', y='Growth_Total Net Premium Income',hue='sector')
    sns.lineplot(ax=axes[1, 0], data=dfChart, x='date', y='Growth_Premium Income',hue='sector')
    sns.lineplot(ax=axes[1, 1], data=dfChart, x='date', y='Growth_Total Claims and Benefits',hue='sector')
    sns.lineplot(ax=axes[1, 2], data=dfChart, x='date', y='Growth_Total Operating Expenses',hue='sector')
    #sns.lineplot(ax=axes[3, 0], data=dfChart, x='date', y='Growth_Total Net Premium Income',hue='sector')
    axes[0,0].get_legend().remove()
    axes[0,1].get_legend().remove()
    axes[0,2].get_legend().remove()
    axes[1,0].get_legend().remove()
    axes[1,1].get_legend().remove()
    axes[1,2].get_legend().remove()

    plt.subplots_adjust(hspace=0.275,wspace=0.325)
    plt.legend(loc="upper right", bbox_to_anchor=(1, 1))
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

def get_data_insurance():
    conn = create_connection(db_insurance_file)
    df = pd.read_sql_query("select * from life_non_life order by Periode", conn)
    return df


def get_basic_information():
    conn = create_connection(db_direktori_aj)
    query="select * from Asuransi_Jiwa order by report_date"
    df_aj = pd.read_sql_query(query,conn)
    df_aj['sektor'] = 'Asuransi Jiwa'
    df_aj['Email 1'] = ''
    conn.close()
    
    conn = create_connection(db_direktori_au)
    query="select * from Asuransi_Umum order by report_date"
    df_au = pd.read_sql_query(query,conn)
    df_au['sektor'] = 'Asuransi Umum'
    conn.close()

    conn = create_connection(db_direktori_reas)
    query="select * from Reasuransi order by report_date"
    df_re = pd.read_sql_query(query,conn)
    df_re['sektor'] = 'Reasuransi'
    df_re['Kota']=df_re['Nama Kota']
    conn.close()

    conn = create_connection(db_direktori_aw)
    query="select * from Asuransi_Wajib order by report_date"
    df_wa = pd.read_sql_query(query,conn)
    df_wa['sektor'] = 'Asuransi Wajib'
    df_wa['Kota']=df_wa['Nama Kota']
    conn.close()

    conn = create_connection(db_direktori_as)
    query="select * from Asuransi_Sosial order by report_date"
    df_so = pd.read_sql_query(query,conn)
    df_so['sektor'] = 'Asuransi Sosial'
    df_so['Kota']=df_so['Nama Kota']
    conn.close()

    columns =['Nama Perusahaan', 'Jenis Kantor', 'No Izin', 'Tanggal Izin', 'Alamat', 'No Telp', 'Kota', 'Jenis Perusahaan', 'Website', 'Email', 'Email 1','created_date', 'report_date','sektor']
    df_aj=df_aj[columns]
    df_au=df_au[columns]
    df_re=df_re[columns]
    df_wa=df_wa[columns]
    df_so=df_so[columns]
    df = pd.concat([df_aj,df_au,df_re,df_wa,df_so],axis=0)
    return df

def get_pertumbuhan_industri_asuransi():
    df=get_basic_information()
    # Groupby multiple columns
    result = df.groupby(['report_date','sektor']).agg({'Nama Perusahaan': 'count'})
    return result

if __name__=="__main__":
    #conn = create_connection(db_insurance_file)
    #df = pd.read_sql_query("select * from life_non_life order by Periode", conn)
    #GrowthIndustri(df)
    #RasioIndustri(df)
    df=get_basic_information()
    print(df)
    '''
    df = get_data_kantor()
    '''
    
    fig.show()
    #print(df)