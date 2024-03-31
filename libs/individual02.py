import pandas as pd
import sqlite3
import json

db_FS_RL_AJ = './datasets/ASURANSI.db'
db_FS_RL_AU ='./datasets/ASURANSI_UMUM.db'

ratio=['r_expense', 'r_claim','r_income', 'r_yield investasi', 'r_modal', 'ROA', 'ROE', 'RKI']
ratio_name=['rasio beban','rasio claim','rasio pendapatan','rasio yield investasi','rasio modal','ROA','ROE','RKI']


def get_ratio_name():
    return ratio_name

def get_ratio_key():
    return ratio

def get_ratio_by_name(rat_name):
    for idx,r in enumerate(ratio_name):
        if r==rat_name:
            return ratio[idx]            


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


def init_connectin():
     conn_AJ = create_connection(db_FS_RL_AJ)
     conn_AU = create_connection(db_FS_RL_AU)
     return conn_AJ,conn_AU

def get_datas():
    conn_AJ, conn_AU=init_connectin()
    query = 'select * from NERACA order by report_date asc'
    df_FS_AJ = pd.read_sql_query(query,conn_AJ)
    df_FS_AU = pd.read_sql_query(query,conn_AU)
    
    query = 'select * from LABARUGI order by report_date asc'
    df_RL_AJ = pd.read_sql_query(query,conn_AJ)
    query = 'select * from LABARUGIMASTER order by report_date asc'
    df_RL_AU = pd.read_sql_query(query, conn_AU)

    df_AJ = pd.merge(df_FS_AJ,df_RL_AJ, on=['NAME OF COMPANY', 'REPORT_DATE'])
    df_AJ["sektor"]='life-insurance'

    df_AU = pd.merge(df_FS_AU,df_RL_AU, on=['NAME OF COMPANIES', 'REPORT_DATE'])
    df_AU["sektor"]='non-life-insurance'

    dfall_AJ=df_AJ.copy()
    dfall_AU=df_AU.copy()

    dfall_AJ['r_expense']=dfall_AJ['TOTAL EXPENSES']/dfall_AJ['TOTAL ASSETS']
    dfall_AJ['r_claim']=dfall_AJ['NET CLAIM EXPENSES']/dfall_AJ['TOTAL ASSETS']
    dfall_AJ['r_income']=dfall_AJ['TOTAL INCOME']/dfall_AJ['TOTAL ASSETS']
    dfall_AJ['r_yield investasi']=dfall_AJ['INVESTMENT YIELDS']/dfall_AJ['INVESTMENTS']
    dfall_AJ['r_modal']=dfall_AJ['EQUITIES']/dfall_AJ['TOTAL ASSETS']
    dfall_AJ['ROA']=dfall_AJ['EARNING BEFORE TAX']/dfall_AJ['TOTAL ASSETS']
    dfall_AJ['ROE']=dfall_AJ['EARNING BEFORE TAX']/dfall_AJ['EQUITIES']
    #dfall_AJ['net revenue']=dfall_AJ['EARNING AFTER TAX']/dfall_AJ['NET EARNED PREMIUM']
    dfall_AJ['RKI']=dfall_AJ['INVESTMENTS']/dfall_AJ['TOTAL RESERVES']
    dfall_AJ['nama']=dfall_AJ['NAME OF COMPANY']

    cols=['OPERATIONAL EXPENSES','TOTAL ASSETS','INVESTMENT INCOME','OTHER INCOME','EQUITY',
        'UNDERWRITING SURPLUS','INVESTMENT INCOME','OTHER COMPREHENSIVE INCOME',
        'PREMIUM RESERVE','UNEARNED PREMIUM RESERVE','CLAIM RESERVE','CATASTHROPIC RESERVE','INVESTMENT']

    for col in cols:
        dfall_AU[col]=dfall_AU[col].astype('float')

    dfall_AU['r_expense']=dfall_AU['OPERATIONAL EXPENSES']/dfall_AU['TOTAL ASSETS']
    #dfall_AU['r_claim']=dfall_AU['NET CLAIM EXPENSES']/dfall_AU['TOTAL ASSETS']
    dfall_AU['r_income']=(dfall_AU['INVESTMENT INCOME'] + dfall_AU['OTHER INCOME'])/dfall_AU['TOTAL ASSETS']
    #dfall_AU['r_yield investasi']=dfall_AU['INVESTMENT YIELDS'].astype('float')/dfall_AU['INVESTMENTS'].astype('float')
    dfall_AU['r_modal']=dfall_AU['EQUITY']/dfall_AU['TOTAL ASSETS']
    dfall_AU['EARNING BEFORE TAX'] = (dfall_AU['UNDERWRITING SURPLUS'] + dfall_AU['INVESTMENT INCOME'] + dfall_AU['OTHER INCOME'] + dfall_AU['OTHER COMPREHENSIVE INCOME'])
    dfall_AU['ROA']=dfall_AU['EARNING BEFORE TAX']/dfall_AU['TOTAL ASSETS']
    dfall_AU['ROE']=dfall_AU['EARNING BEFORE TAX']/dfall_AU['EQUITY']

    #dfbll['net revenue']=dfbll['EARNING AFTER TAX']/dfbll['NET EARNED PREMIUM']
    dfall_AU['TOTAL RESERVES'] = dfall_AU['PREMIUM RESERVE'] + dfall_AU['UNEARNED PREMIUM RESERVE'] + dfall_AU['CLAIM RESERVE'] + dfall_AU['CATASTHROPIC RESERVE']
    dfall_AU['RKI']=dfall_AU['INVESTMENT']/dfall_AU['TOTAL RESERVES']
    dfall_AU['nama']=dfall_AU['NAME OF COMPANIES']

    dfall1= dfall_AJ.iloc[:,[1,2,5,31,32,33,34,35,36]]
    dfall1['nama']=dfall_AJ['NAME OF COMPANY']

    dfbll1= dfall_AU.iloc[:,[1,2,5,24,25,26,27,29,30,32]]
    dfbll1['nama']=dfall_AU['NAME OF COMPANIES']

    return dfall_AJ,dfall_AU,dfall1,dfbll1

def draw_komparasi_rasio(df,var_atas, var_bawah, hue,size,x_label,y_label, title):
    import plotly
    import plotly.express as px

    fig = px.scatter(df, x=var_atas, y=var_bawah, title=title,color=hue,size=size,log_x=True,size_max=60)
    fig.update_layout(showlegend=False)
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def drawPair(df,dimensions,hue):
    import plotly
    import plotly.express as px
    
    fig = px.scatter_matrix(df,dimensions=dimensions, color=hue)
    fig.show()

    '''
    g = sns.PairGrid(df, corner=True)
    g.map_upper(sns.scatterplot)
    g.map_diag(sns.histplot)
    g.map_lower(sns.scatterplot)
    plt.show()
    '''

def drawPairPlot(df,hue,title):
    import plotly
    import plotly.express as px
    
    fig = px.scatter(df,color=hue,title=title)
    fig.show()
    
def drawRegressionPlot(df,x,y,hue,size,title):
    import plotly
    import plotly.express as px
    #fig = px.scatter(df, x=x, y=y, color=hue, trendline="lowess",trendline_options=dict(frac=0.2))
    #fig = px.scatter(df, x=x, y=y, color=hue, trendline="ols",trendline_options=dict(log_x=True))
    fig = px.scatter(df, x=x, y=y, color=hue, size=size,trendline="ols")
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def drawLmPlot(df,x,y,hue,title):
    import seaborn as sns
    import matplotlib.pyplot as plt

    # For lmplot
    g = sns.lmplot(x=x, y=y, hue=hue, data=df)
    g.set(title=title)
    plt.show()

def cluster(df,x,y,x_label,y_label,title):
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
    
    from sklearn.datasets import make_blobs
    from sklearn.cluster import KMeans
    #print(df[x],df[y])
    '''
    data1=pd.DataFrame([df[x], df[y]])
    data1 = data1.transpose()
    X = data1.values
    
    kmeans = KMeans(n_clusters=4)
    kmeans.fit(X)

    # Get cluster centers and labels
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    '''

    selected_data = df[[x, y]].copy()

    kmeans = KMeans(n_clusters=4, init='k-means++')
    kmeans = kmeans.fit(selected_data)
    df['cluster'] = kmeans.labels_
    centroids = kmeans.cluster_centers_

    fig = px.scatter(df, x=x, y=y, color='cluster', 
                 hover_data=['nama', 'sektor'], template='ggplot2',title=title)
    fig.add_trace(go.Scatter(x=centroids[:,0], y=centroids[:,1],  text="Centroid",mode='markers', marker=dict(size=10)))

    #fig.show()
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

    # Visualize clustering results
   
if __name__=="__main__":
    df_aj,df_au,df1,df2 = get_datas()

    #print(df1)
    #dimensions=['r_expense', 'r_claim', 'r_income', 'r_yield investasi', 'r_modal']
    #drawPair(df1,dimensions,'sektor')
    #dimensions=['r_expense','r_income', 'r_modal']
    #print(df1['sektor'])    
    #drawPair(df2,dimensions,'sektor')
    #print(df2['sektor'])
    #draw_komparasi_rasio(df_aj,'r_modal','r_yield investasi','sektor','TOTAL ASSETS', 
    #    'rasio permodalan','rasio pendapatan investasi','Scatterplot with Total Assets')
    
    #df1=df1.append(df2)

    df1 = pd.concat([df1,df2])
    #print(df1.columns)
    dfcll=df1.iloc[:,[0,2,3,4,5,6,7,8,11,12,13]]
    print(dfcll.columns)



    #draw_komparasi_rasio(df1,'r_modal','r_income','sektor','TOTAL ASSETS',
    #    'rasio permodalan','rasio pendapatan','Scatterplot with Total Assets')

    #dimensions=['r_modal', 'r_income']
    #drawPair(df1,dimensions,'sektor')
    drawRegressionPlot(dfcll, 'r_expense','r_modal','sektor','TOTAL ASSETS','modal vs profitabilitas')
    #drawLmPlot(dfcll, 'r_expense','r_modal','sektor','Scatterplot with Regression Analysis for Multiple Groups')
    #drawLmPlot(dfcll, 'r_income','r_expense','sektor','Scatterplot with Regression Analysis for Multiple Groups')
    #draw_komparasi_rasio(df_au,'r_modal','r_yield investasi','TOTAL ASSETS', 
    #    'rasio permodalan','rasio pendapatan investasi','Scatterplot with Total Assets')
    cluster(df_aj,'r_modal','r_income','modal','pendapatan')
    #cluster(df_au,'r_modal','r_income','modal','profitabilitas')
    #print(df)

