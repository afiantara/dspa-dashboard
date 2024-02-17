# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request,jsonify,session
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db
from apps.projects.models import UpdateProgress,Projects,UpdateProgressHist
import json
from apps.home.news import getnews,sentiment_analysis,saveplot,plotly_visualize
from flask_paginate import Pagination,get_page_args
import os
from  libs.trends import get_trend

def getListProyek():
    list_code=[]
    datas=[]
    results = db.session.query(Projects).all()
    for result in results:
        list_code.append(result.code_project)
        progress = UpdateProgress.query.filter_by(code_project=result.code_project).first()
        if not progress is None:
            result.plan_project = progress.plan_project
            result.real_project = progress.real_project
            result.performance=(result.real_project/result.plan_project)*100
    
    db.session.commit()

    return results,list_code

@blueprint.route('/getSCurve', methods=['GET', 'POST'])
@login_required
def getSCurve():
    print('getSCurve')
    if request.method == "POST":
        code= request.get_json()
        print(f'code: ',code)
        
        all = UpdateProgressHist.query.order_by(UpdateProgressHist.tgl_update).all()
        all = db.session.query(UpdateProgressHist).filter_by(code_project=code).all()
        db.session.commit()
    
    labels=[]
    dataset1=[]
    dataset2=[]

    for item in all:
        labels.append(item.tgl_update.strftime("%Y-%m-%d"))
        dataset1.append(item.plan_project)
        dataset2.append(item.real_project)
    # assume this is defined somewhere else, like a database 
    chart_data = {
        "labels": labels,
        "dataset1": dataset1,
        "dataset2": dataset2
    } 
    return chart_data

@blueprint.route('/index')
@login_required
def index():
    print('home-routes-index')
    proyeks,codes = getListProyek()
    return render_template('home/index.html', segment='index',proyek=proyeks,code=codes)

@blueprint.route('/<template>')
@login_required
def route_template(template):
    print('route_template')
    try:
        print(f'home-routes-route_template',template)    
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'
        return segment

    except:
        return None



def sentimen_analisis(df,model,categories):
    wordcloud =sentiment_analysis(df,model,categories)
    target= os.path.join('apps','static','assets','img','new_plot.png')
    saveplot(wordcloud,target)

def get_news(news,offset=0, per_page=5):
    return news[offset: offset + per_page]

@blueprint.route('/news',methods= ['GET','POST'])
@login_required
def news():
    selected_model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'
    my_dict = {"MoritzLaurer/mDeBERTa-v3-base-mnli-xnli": "tab1", "lxyuan/distilbert-base-multilingual-cased-sentiments-student": "tab2", "bert-base-indonesian-1.5G-finetuned-sentiment-analysis-smsa": "tab3"} 
    return render_template('home/news.html',         
        my_dict=my_dict,
        selected_model=selected_model,
        )
    

@blueprint.route('/search_news',methods= ['GET','POST'])
@login_required
def search_news():
    
    if request.method=='POST':
        keywords_ori=request.form['search']
        keywords = keywords_ori.split(',')
        categories_ori=request.form['category']
        categories=categories_ori.split(',')
        selected_model=request.form['model']
        
        news_ori = getnews(keywords)
        news_ori = news_ori.sort_values(by=['date'],ascending=False)
        news = news_ori.to_dict(orient='records')
        page, per_page, offset = get_page_args(page_parameter='page',
                                        per_page_parameter='per_page')
        total = len(news)
        pagination_news = get_news(news,offset=offset, per_page=per_page)
    
        pagination = Pagination(page=page, per_page=per_page, total=total,
                        css_framework='bootstrap4')
    
    if not selected_model:
        selected_model='MoritzLaurer/mDeBERTa-v3-base-mnli-xnli'
    else:
        sentimen_analisis(news_ori,selected_model,categories)    
    
    my_dict = {"MoritzLaurer/mDeBERTa-v3-base-mnli-xnli": "tab1", "lxyuan/distilbert-base-multilingual-cased-sentiments-student": "tab2", "bert-base-indonesian-1.5G-finetuned-sentiment-analysis-smsa": "tab3"} 
    
    graphJSON=plotly_visualize(news_ori)
    
    return render_template('home/news.html',keywords=keywords_ori,
        news=pagination_news,
        page=page,
        per_page=per_page,
        pagination=pagination,
        my_dict=my_dict,
        selected_model=selected_model,
        category=categories_ori,
        graphJSON=graphJSON
        )

@blueprint.route('/trend',methods= ['GET','POST'])
@login_required
def trend():
    return render_template('home/trend.html')

@blueprint.route('/search_trend',methods= ['GET','POST'])
@login_required
def search_trend():
    if request.method=='POST':
        keyword_orig= request.form['keywords']
        print(f'keyword:',keyword_orig)
        keywords = keyword_orig.split(',')
        data_overtime,graphJSON_overtime,data_geo,graphJSON_geo,data_q,data_search,iframe= get_trend(keywords,'today 5-y','DMA','indonesia')
        overtime = data_overtime.to_dict(orient='records')
    
    return render_template('home/trend.html',
        keywords = keyword_orig,
        overtime = overtime,
        graphJSON_overtime = graphJSON_overtime,
        graphJSON_geo=graphJSON_geo,
        data_geo = data_geo,
        data_q = data_q,
        data_search = data_search,
        iframe=iframe,
        )