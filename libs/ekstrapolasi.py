import sqlite3
import pandas as pd

db_kinerja ='./datasets/KINERJA.db'

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

def getTOP10Equity(isJiwa=True):
    conn = create_connection(db_kinerja)
    if isJiwa:
        query="SELECT REPORT_DATE,TRIM(NAMA_PERUSAHAAN) AS NAMA_PERUSAHAAN,cast(MODAL_SENDIRI_JUMLAH_MODAL_SENDIRI as float) AS EQUITY FROM ASURANSI_JIWA WHERE REPORT_DATE='2022-12-31' order by cast(MODAL_SENDIRI_JUMLAH_MODAL_SENDIRI as float) desc limit 10 "
    else:
        query="SELECT REPORT_DATE,TRIM(NAMA_PERUSAHAAN) AS NAMA_PERUSAHAAN,cast(MODAL_SENDIRI as float) AS EQUITY FROM ASURANSI_UMUM WHERE REPORT_DATE='2022-12-31' order by cast(MODAL_SENDIRI as float) desc limit 10 "
    df = pd.read_sql_query(query,conn)
    return df


def getEquity(company_name,isJiwa=True):
    conn = create_connection(db_kinerja)
    if isJiwa:
        query="SELECT REPORT_DATE,TRIM(NAMA_PERUSAHAAN) as NAMA_PERUSAHAAN,cast(MODAL_SENDIRI_JUMLAH_MODAL_SENDIRI as float) AS EQUITY FROM ASURANSI_JIWA WHERE TRIM(NAMA_PERUSAHAAN)='{}' order by REPORT_DATE ASC".format(company_name)
    else:
        query="SELECT REPORT_DATE,TRIM(NAMA_PERUSAHAAN) as NAMA_PERUSAHAAN,cast(MODAL_SENDIRI as float) AS EQUITY FROM ASURANSI_UMUM WHERE TRIM(NAMA_PERUSAHAAN)='{}' order by REPORT_DATE ASC".format(company_name)
    print(query)
    df = pd.read_sql_query(query,conn)
    df.loc[len(df.index)] = ['2023-12-31', company_name, 0] 
    df.loc[len(df.index)] = ['2024-12-31', company_name, 0] 
    df.loc[len(df.index)] = ['2025-12-31', company_name, 0]
    df.loc[len(df.index)] = ['2026-12-31', company_name, 0]
    df.loc[len(df.index)] = ['2027-12-31', company_name, 0]
    print(df)
    return df

def extrapolate(df,lendata,pred_periode=6):
    df1 = df.copy() 
    
    df1['t-1'] = 0.00
    df1[ 't-2' ] = 0.00
    df1[ 't-3' ] = 0.00
    for i in range(1,(len(df1[ 'EQUITY' ])-pred_periode)):
        df1[ 't-1' ][i] = df1[ 'EQUITY' ][i-1] 
        df1[ 't-2' ][i] = df1[ 't-1' ][i-1] 
        df1[ 't-3' ][i] = df1[ 't-2' ][i-1]
    #print(df1)
    xval=df1[ 1 : lendata ][[ 't-1' , 't-2' , 't-3' ]] 
    yval=df1[ 1 : lendata ][[ 'EQUITY' ]] 
    #print(xval)
    #print(yval)
    import sklearn.linear_model as skl 
    model = skl.LinearRegression() 
    
    model.fit(xval,yval) 
    
    xval1 = df1[: lendata ][[ 't-1' , 't-2' , 't-3' ]] 
    #print(xval1)
    pred = model.predict(xval1) 
    #print(pred)
    pred1 = pd.DataFrame(pred, columns = [ 'pred' ]) 
    #pred1 = pd.DataFrame(pred, columns = [ 'pred' ]) 
    #print(pred1)
    df1[ 'Forecast Fit' ] = 0.00

    for i in range ( 0 ,( len (pred1[ 'pred' ]))): 
        df1['Forecast Fit'][i] = pred1['pred'][i].round(2)
    
    for i in range(lendata-3,lendata-3+pred_periode):
        df1['Forecast Fit'][i+3] = model.intercept_[0] + model.coef_[0][0]*df1['EQUITY'][i+2] + model.coef_[0][1]*df1['EQUITY'][i+1] + model.coef_[0][2]*df1['EQUITY'][i]
        df1['EQUITY'][i+3] =  df1['Forecast Fit'][i+3]

    df1.drop(['t-1','t-2','t-3'],axis=1,inplace=True)
    
    df1['Actual1'] = df1['EQUITY']
    
    for i in range(lendata-3,lendata-3+pred_periode):
        df1['EQUITY'][i+3] =  ""
    
    df1['Forecast Fit'] = round((df1['Forecast Fit']),2)
    
    df2 = df1.copy()
    
    df2.drop(['Actual1'],axis=1,inplace=True)
    
    df2['Estimate Error'] = 0.000
    for i in range(0,lendata):
        df2['Estimate Error'][i] = df2['Forecast Fit'][i] - df2['EQUITY'][i]
    
    print(df2)
    for i in range(lendata,lendata+pred_periode):
        df2['Estimate Error'][i] =  ""
        
    print(df2)
    return df1,df2

def visualize(company,df,min,max):
    import matplotlib.pyplot as plt
    import numpy as np
    import plotly
    import plotly.express as px
    import plotly.graph_objects as go
    
    plt.figure(figsize=(13,7))
    fontsize=15
    
    #plt.title("Nonlinear Extrapolation of Equities - Actual vs. Forecast of {}".format(company),fontsize=fontsize)
    #ax = plt.axes()
    #x.set_facecolor("yellow")
    
    #Actual = np.array(df.Actual1)
    #Forecast = np.array(df['Forecast Fit'])
    # plotly figure setup
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df['REPORT_DATE'], y=df['EQUITY'].values, mode='markers'))
    fig.add_trace(go.Scatter(name='line of best fit', x=df['REPORT_DATE'], y=df['Forecast Fit'], mode='lines'))

    # plotly figure layout
    fig.update_layout(xaxis_title = 'PERIODE', yaxis_title = 'EQUITY')
    fig.update_layout(
        title = "Nonlinear Extrapolation of Equities - Actual vs. Forecast of {}".format(company)
    )
    fig.show()


    #plt.plot(Forecast,marker = 'o', color="deeppink", label="Forecast")
    #plt.plot(Actual, marker = 'o', color="blue", label="Actual")
    #fig.legend(loc="center right")
    #plt.xlim(0, df.shape[0])
    #plt.ylim(min, max)
    #plt.show()
def createFrame():
    data = [[1, 1.00], [2, 6.73], [3, 20.52],[4, 45.25],[5, 83.59],[6, 138.01],[7, 210.87],[8, 304.44],[9, 420.89],[10, 562.34],[11, 730.85],[12, 928.43],
            [13, 0.00],[14, 0.00]]#,[15, 0.00],[16, 0.00],[17, 0.00],[18, 0.00]]
    columns=['REPORT_DATE', 'EQUITY']
    df = pd.DataFrame(data, columns=columns)
    return df

def createFrame1():
    data = [[1, 1066111.00], [2, 1288588.00], [3, 1550979.00],[4, 1495844.00],[5, 1384284.00],[6, 1121514.00],[7, 1237305.00],[8, 7234540.00],
            [9, 0.00],[10, 0.00]]#,[15, 0.00],[16, 0.00],[17, 0.00],[18, 0.00]]
    columns=['REPORT_DATE', 'EQUITY']
    df = pd.DataFrame(data, columns=columns)
    return df

def linear_extrapolate():
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    # Set a random seed for reproducibility
    np.random.seed(42)

    # Generate some synthetic data
    X = np.array(sorted(list(range(5))*20)) + np.random.normal(size=100, scale=0.5)
    y = X + np.random.normal(size=100, scale=1)
    # Reshape X to a 2D array
    X = X.reshape(-1,1)
    # Create and train the model
    model = LinearRegression()
    model.fit(X, y)

    # Generate some future points for extrapolation
    X_future = np.array(range(-2, 10)).reshape(-1, 1)
    #print(X_future)
    # Predict their corresponding y values
    y_future = model.predict(X_future)

    # Plot the original data
    plt.scatter(X, y, color = "blue")

    # Plot the line of best fit
    plt.plot(X_future, y_future, color = "red")

    # Plot the extrapolated points
    plt.scatter(X_future, y_future, color = "green")

    # Set title
    plt.title('Linear Regression Extrapolation')

    # Show the plot
    plt.show()
    
if __name__=="__main__":
    '''
    df =createFrame1()
    print(df)
    lendata=df.shape[0]-2
    df1,df2=extrapolate(df,lendata,2)
    visualize('',df1,-500,5000)
    '''
    isJiwa=False
    df=getTOP10Equity(isJiwa)
    companies = df['NAMA_PERUSAHAAN'].values
    print(companies)
    df_all = pd.DataFrame()
    #print(companies)
    for company in companies:
        #if company!='SUN LIFE FINANCIAL INDONESIA': continue
        df=getEquity(company,isJiwa)
        #print(df.shape[0])
        lendata=df.shape[0]-5
        #print(df[:lendata])
        #print(lendata)
        df1,df2=extrapolate(df,lendata,5)
        #print(df1)
        for i in range(lendata,lendata+5):
            df['EQUITY'][i] = df1['Forecast Fit'][i]
        print(df)
        #visualize(company, df1,-100000,50000000)
        df_all=pd.concat([df_all,df])
    
    if isJiwa==True:
        df_all.to_csv('./datasets/equitas_aj.csv')
    else:
        df_all.to_csv('./datasets/equitas_au.csv')
    