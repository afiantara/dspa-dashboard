from . import blueprint
from flask import render_template,redirect,jsonify,request
from flask_login import login_required
from dash_app import individual, industrial,industrial02,individual02
import json
from libs.individual import *
from libs.individual02 import *

@blueprint.route('/getCompareRatio', methods=['GET', 'POST'])
@login_required
def getCompareRatio():
    print('getCompareRatio')
    if request.method=='POST':
        data = request.get_json()
        left_ratio =  data ["left_ratio"]
        right_ratio =  data["right_ratio"]

    df_aj,df_au,df1,df2 = get_datas()
    df1 = pd.concat([df1,df2])

    dfcll=df1.iloc[:,[0,2,3,4,5,6,7,8,11,12,13]]

    left_ratio_code=get_ratio_by_name(left_ratio)
    right_ratio_code=get_ratio_by_name(right_ratio)
    json_graph=drawRegressionPlot(dfcll,  left_ratio_code,right_ratio_code,'sektor','TOTAL ASSETS','{} vs {}'.format(left_ratio,right_ratio))
    data_json = {
        'json_result':json_graph
    } 

    return data_json

@blueprint.route('/individual')
@login_required
def individual():
    #from libs.individual import get_ratios,PlotRBC,PlotRKI,Top10,PlotInsolvenRBC,PlotInsolvenRKI,PlotAllRasio,get_periode
    import plotly
    import plotly.express as px
    df_ori = get_ratios()
    dfRBC =PlotRBC(df_ori)
    dfRKI = PlotRKI(df_ori)

    fig = px.scatter(dfRBC, x="NAMA_PERUSAHAAN", y='RBC', title='Distribusi RBC Perusahaan Asuransi',color='sector')
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title='x', visible=False, showticklabels=False)
    fig.add_hline(y=120)
    graphJSON_RBC = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.scatter(dfRKI, x="NAMA_PERUSAHAAN", y='RKI', title='Distribusi RKI Perusahaan Asuransi',color='sector')
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title='x', visible=False, showticklabels=False)
    fig.add_hline(y=100)
    graphJSON_RKI = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #top10 Asuransi Jiwa
    dfRBC,dfRKI,yr = Top10(df_ori,'life')
    fig = px.bar(dfRBC, x="RBC", y='NAMA_PERUSAHAAN', title='Top 10 Gainer Asuransi Jiwa RBC - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopRBC = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    fig = px.bar(dfRKI, x="RKI", y='NAMA_PERUSAHAAN', title='Top 10 Gainer Asuransi Jiwa RKI - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopRKI = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    dfRBC,dfRKI,yr = Top10(df_ori,'life',True)
    fig = px.bar(dfRBC, x="RBC", y='NAMA_PERUSAHAAN', title='Top 10 Looser Asuransi Jiwa RBC - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopLRBC = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    fig = px.bar(dfRKI, x="RKI", y='NAMA_PERUSAHAAN', title='Top 10 Looser Asuransi Jiwa RKI - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopLRKI = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #top10 Asuransi Umum
    dfRBC,dfRKI,yr = Top10(df_ori,'non-life')
    fig = px.bar(dfRBC, x="RBC", y='NAMA_PERUSAHAAN', title='Top 10 Gainer Asuransi Umum RBC - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopRBCAU = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    fig = px.bar(dfRKI, x="RKI", y='NAMA_PERUSAHAAN', title='Top 10 Gainer Asuransi Umum RKI - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopRKIAU = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    dfRBC,dfRKI,yr = Top10(df_ori,'non-life',True)
    fig = px.bar(dfRBC, x="RBC", y='NAMA_PERUSAHAAN', title='Top 10 Looser Asuransi Umum RBC - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopLRBCAU = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    fig = px.bar(dfRKI, x="RKI", y='NAMA_PERUSAHAAN', title='Top 10 Looser Asuransi Umum RKI - Tahun {}'.format(yr),color='sector',orientation='h')
    fig.update_layout(showlegend=False)
    graphJSON_TopLRKIAU = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #insolven  RBC or RKI <120
    dfInsolven=PlotInsolvenRBC(df_ori)
    fig = px.scatter(dfInsolven, x="NAMA_PERUSAHAAN", y='RBC', title='Perusahaan Asuransi yang pernah RBC < 120%',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_InsolvenRBC = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
    dfInsolven=PlotInsolvenRKI(df_ori)
    fig = px.scatter(dfInsolven, x="NAMA_PERUSAHAAN", y='RKI', title='Perusahaan Asuransi yang pernah RKI < 100%',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_InsolvenRKI = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #plot all ratios
    df = PlotAllRasio(df_ori)
    fig = px.bar(df, x="yr", y='RBC', title='Rata-Rata Rasio RBC Tahunan',color='sector',barmode='group')
    fig.update_layout(showlegend=False)
    graphJSON_rasioRBCAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.bar(df, x="yr", y='RKI', title='Rata-Rata Rasio RKI Tahunan',color='sector',barmode='group')
    fig.update_layout(showlegend=False)
    graphJSON_rasioRKIAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.bar(df, x="yr", y='RLiq', title='Rata-Rata Rasio Liqiuidity Tahunan',color='sector',barmode='group')
    fig.update_layout(showlegend=False)
    graphJSON_rasioLiqAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)    
    
    fig = px.bar(df, x="yr", y='RPHI', title='Rata-Rata Rasio Perimbangan Hasil Investasi dengan Pendapatan Premi Netto Tahunan',color='sector',barmode='group')
    fig.update_layout(showlegend=False)
    graphJSON_rasioRPHIAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.bar(df, x="yr", y='RBPN', title='Rata-Rata Rasio Beban dengan Pendapatan Premi Netto Tahunan',color='sector',barmode='group')
    fig.update_layout(showlegend=False)
    graphJSON_rasioRBPNAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #dropdown year
    years =get_periode(df_ori)
    print(years)


    #analitical rasio
    ratio_names = get_ratio_name()

    #k-means
    df_aj,df_au,df1,df2 = get_datas()
    graph_cluster_aj=cluster(df_aj,'r_modal','r_income','modal','pendapatan','Kmeans Clustering Rasio Perusahaan Asuransi Jiwa')
    graph_cluster_au=cluster(df_au,'r_modal','r_income','modal','pendapatan','Kmeans Clustering Rasio Perusahaan Asuransi Umum')

    #[]
    return render_template('dash_app/individual02.html',
        json_RBC = graphJSON_RBC,
        json_RKI=graphJSON_RKI,
        json_Top10RBC=graphJSON_TopRBC,
        json_Top10RKI=graphJSON_TopRKI,
        json_Top10LRBC=graphJSON_TopLRBC,
        json_Top10LRKI=graphJSON_TopLRKI,
        json_Top10RBCAU=graphJSON_TopRBCAU,
        json_Top10RKIAU=graphJSON_TopRKIAU,
        json_Top10LRBCAU=graphJSON_TopLRBCAU,
        json_Top10LRKIAU=graphJSON_TopLRKIAU,
        json_InsolvenRBC=graphJSON_InsolvenRBC,
        json_InsolvenRKI=graphJSON_InsolvenRKI,
        json_rasioRBCAvg=graphJSON_rasioRBCAvg,
        json_rasioRKIAvg=graphJSON_rasioRKIAvg,
        json_rasioLiqAvg=graphJSON_rasioLiqAvg,
        json_rasioRPHIAvg=graphJSON_rasioRPHIAvg,
        json_rasioRBPNAvg=graphJSON_rasioRBPNAvg,
        years=years,
        ratio_names=ratio_names,
        json_graph_cluster_aj=graph_cluster_aj,
        json_graph_cluster_au=graph_cluster_au
        )


@blueprint.route('/getratio',methods= ['GET','POST'])
@login_required
def getratio():
    from libs.individual import PlotAllRasio,get_periode,get_ratios
    import plotly
    import plotly.express as px
    if request.method=='POST':
        year = request.get_json()
        df_ori = get_ratios()
        df = PlotAllRasio(df_ori,year)
    
        fig = px.bar(df, x="yr", y='RBC', title='Rata-Rata Rasio RBC Tahunan',color='sector',barmode='group')
        fig.update_layout(showlegend=False)
        graphJSON_rasioRBCAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(df, x="yr", y='RKI', title='Rata-Rata Rasio RKI Tahunan',color='sector',barmode='group')
        fig.update_layout(showlegend=False)
        graphJSON_rasioRKIAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(df, x="yr", y='RLiq', title='Rata-Rata Rasio Liqiuidity Tahunan',color='sector',barmode='group')
        fig.update_layout(showlegend=False)
        graphJSON_rasioLiqAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)    
        
        fig = px.bar(df, x="yr", y='RPHI', title='Rata-Rata Rasio Perimbangan Hasil Investasi dengan Pendapatan Premi Netto Tahunan',color='sector',barmode='group')
        fig.update_layout(showlegend=False)
        graphJSON_rasioRPHIAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

        fig = px.bar(df, x="yr", y='RBPN', title='Rata-Rata Rasio Beban dengan Pendapatan Premi Netto Tahunan',color='sector',barmode='group')
        fig.update_layout(showlegend=False)
        graphJSON_rasioRBPNAvg = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    data_rasio = {
        'json_rasioRBCAvg':graphJSON_rasioRBCAvg,
        'json_rasioRKIAvg':graphJSON_rasioRKIAvg,
        'json_rasioLiqAvg':graphJSON_rasioLiqAvg,
        'json_rasioRPHIAvg':graphJSON_rasioRPHIAvg,
        'json_rasioRBPNAvg':graphJSON_rasioRBPNAvg
    } 
    return data_rasio

@blueprint.route('/do_map_sebaran_kc',methods= ['GET','POST'])
@login_required
def do_map_sebaran_kc():
    if request.method=='POST':
        from libs.map_industrial import do_map
        iframe = do_map()

    map_data = {
        "iframe": iframe
    } 
    return map_data    

@blueprint.route('/app3')
@login_required
def app3():
    from libs.industry import get_data_insurance,plotGrowthIndustry,plotRasioIndustri,get_pertumbuhan_industri_asuransi
    import plotly
    import plotly.express as px
    df_ori = get_data_insurance()
    df = plotGrowthIndustry(df_ori)
    dfRasio = plotRasioIndustri(df_ori)

    fig = px.line(df, x="date", y='Growth_Total Assets', title='Growth Total Assets',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalAssetGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df, x="date", y='Growth_Total Investment', title='Growth Total Investment',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalInvestmentGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df, x="date", y='Growth_Total Net Premium Income', title='Growth Total Net Premium Income',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalNetPremIncomeGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df, x="date", y='Growth_Premium Income', title='Growth Premium Income',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalPremIncomeGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df, x="date", y='Growth_Total Claims and Benefits', title='Growth Total Claims and Benefits',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalClaimBenefitGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(df, x="date", y='Growth_Total Operating Expenses', title='Growth Total Operating Expenses',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_TotalOpExpenseGrowth = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #Rasio
    fig = px.line(dfRasio, x="date", y='ROA', title='ROA',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_ROA = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='ROE', title='ROE',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_ROE = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Investment Yield Ratio', title='Investment Yield Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_InvYieldRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Loss Ratio', title='Loss Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_LossRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Expense Ratio', title='Expense Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_ExpRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Combined Ratio', title='Combined Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_CombinedRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Cession Ratio', title='Cession Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_CessionRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Retention Ratio', title='Retention Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_RetentionRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Net Income Ratio', title='Net Income Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_NetIncomeRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Liquid Ratio', title='Liquid Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_LiquidRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Investment Adequacy Ratio', title='Investment Adequacy Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_InvAdequacyRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    fig = px.line(dfRasio, x="date", y='Premium to Claim Ratio', title='Premium to Claim Ratio',color='sector')
    fig.update_layout(showlegend=False)
    graphJSON_PremToClaimRatio = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    #pertumbuhan pas
    result = get_pertumbuhan_industri_asuransi()
    fig = px.bar(result, x=result.index.get_level_values(0), y="Nama Perusahaan",
             color=result.index.get_level_values(1), 
             text_auto='1.2s')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(barmode='group')
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig.update_layout(
        #title="Pertumbuhan Industri Asuransi",
        xaxis_title="Periode",
        yaxis_title="Jumlah",
        legend_title="Jenis PA/S",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        )
    )
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    #'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    graphJSON_JumlahPAS = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dash_app/industrial02.html', 
                json_totalassetgrowth = graphJSON_TotalAssetGrowth,
                json_totalinvestmentgrowth=graphJSON_TotalInvestmentGrowth,
                json_totalnetpremincomegrowth=graphJSON_TotalNetPremIncomeGrowth,
                json_totalpremincomegrowth=graphJSON_TotalPremIncomeGrowth,
                json_totalclaimbenefitgrowth=graphJSON_TotalClaimBenefitGrowth,
                json_totalopexpensegrowth=graphJSON_TotalOpExpenseGrowth,
                json_ROA=graphJSON_ROA,
                json_ROE=graphJSON_ROE,
                json_InvYieldRatio=graphJSON_InvYieldRatio,
                json_LossRatio=graphJSON_LossRatio,
                json_ExpRatio=graphJSON_ExpRatio,
                json_CombinedRatio=graphJSON_CombinedRatio,
                json_CessionRatio=graphJSON_CessionRatio,
                json_RetentionRatio=graphJSON_RetentionRatio,
                json_NetIncomeRatio=graphJSON_NetIncomeRatio,
                json_LiquidRatio=graphJSON_LiquidRatio,
                json_InvAdequacyRatio=graphJSON_InvAdequacyRatio,
                json_PremToClaimRatio=graphJSON_PremToClaimRatio,
                json_JumlahPAS=graphJSON_JumlahPAS
                )


@blueprint.route('/individual_timeseries',methods= ['GET','POST'])
@login_required
def individual_timeseries():
    from libs.individual import get_companies,get_accounts
    companies_jiwa=get_companies()
    accounts = get_accounts()
    #accounts_jiwa,accounts_umum,companies_jiwa,companies_umum,companies,df1,df2=get_datas()
    return render_template('dash_app/individual03.html',
        companies_jiwa=companies_jiwa,
        accounts=accounts)

@blueprint.route('/individual_au_timeseries',methods= ['GET','POST'])
@login_required
def individual_au_timeseries():
    from libs.individual import get_companies,get_accounts
    companies=get_companies(False)
    accounts = get_accounts(False)
    #accounts_jiwa,accounts_umum,companies_jiwa,companies_umum,companies,df1,df2=get_datas()
    return render_template('dash_app/individual04.html',
        companies=companies,
        accounts=accounts)

@blueprint.route('/compare_individual_jiwa',methods= ['GET','POST'])
@login_required
def compare_individual_jiwa():
    from libs.individual import get_data_by_account_jiwa
    import plotly
    import plotly.express as px

    if request.method=='POST':
        data = request.get_json()
        company =  data ["company"]
        account=  data["account"]

    account_chart=account.split(',')
    account_chart=split_strip(account_chart,2)
    account_chart=account_chart.split(',')

    companies=company.split(',')
    company=split_strip(companies,1)

    accounts=account.split(',')
    account=split_strip(accounts,0)
    df = get_data_by_account_jiwa(company,account)
    fig = px.line(df, x='REPORT_DATE', y=account_chart, title=account,color='NAMA_PERUSAHAAN')
    #fig.update_layout(showlegend=False)
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    data_json = {
        'json_result':graphJSON
    } 
    return data_json

@blueprint.route('/compare_individual_umum',methods= ['GET','POST'])
@login_required
def compare_individual_umum():
    from libs.individual import get_data_by_account_umum
    import plotly
    import plotly.express as px

    if request.method=='POST':
        data = request.get_json()
        company =  data ["company"]
        account=  data["account"]

    account_chart=account.split(',')
    account_chart=split_strip(account_chart,2)
    account_chart=account_chart.split(',')

    companies=company.split(',')
    company=split_strip(companies,1)

    accounts=account.split(',')
    account=split_strip(accounts,0)
    df = get_data_by_account_umum(company,account)
    print(df)
    fig = px.line(df, x='REPORT_DATE', y=account_chart, title=account,color='NAMA_PERUSAHAAN')
    #fig.update_layout(showlegend=False)
    graphJSON = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

    data_json = {
        'json_result':graphJSON
    } 
    return data_json


@blueprint.errorhandler(403)
def access_forbidden(error):
    print('blueprint.errorhandler')
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    print('unauthorized_handler')
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500