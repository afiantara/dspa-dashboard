# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - Agus Afiantara
"""

from flask import render_template, redirect, request, url_for,render_template_string,send_file
from apps import db
from apps.tools import blueprint
from flask_login import login_required
import pygwalker as pyg
import pandas as pd

import dtale
from pycaret.classification import *
import pathlib
import os
from PIL import Image
import base64
import io

@blueprint.route('/')
def route_default():
    print('tools_blueprint.route(/)')
    return redirect(url_for('tools_blueprint.showpyg'))

@blueprint.route('/uploaderpyg', methods = ['GET', 'POST'])
@login_required
def uploaderpyg():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        df = pd.read_csv (f.filename)
        walker = pyg.walk(df, return_html=True,hideDataSourceConfig=False)
        return render_template('tools/pygwalker.html',data=walker)

@blueprint.route('/showpyg')
@login_required
def showpyg():
    print('tools-route_default')
    data = ['welcome']
    df=pd.DataFrame(data,columns=['word'])
    #walker = pyg.walk(df) #, return_html=True, hideDataSourceConfig=False
    walker = pyg.walk(df, return_html=True,hideDataSourceConfig=False)
    return render_template('tools/pygwalker.html',data=walker)

@blueprint.route('/showdtale')
@login_required
def showdtale():
    print('tools-route_default')
    _dtale_server = os.getenv('SERVER_DTALE')
    _dtale_port   = os.getenv('PORT_DTALE')
    _url = '{}:{}'.format(_dtale_server,_dtale_port)
    return render_template('tools/dtale.html',data=_url)

@blueprint.route('/showml')
@login_required
def showml():
    print('tools-showml')
    my_dict = {"Binary Classification": "tab1", "Multiclass Classification": "tab2", "Clustering": "tab3", "Anomaly Detection": "tab4", "Regression": "tab5", "Time Series Forecasting": "tab6"} 
    #is data dengan dataframe kosong
    data = pd.DataFrame()
    return render_template('tools/mlmodel.html',data=data,my_dict=my_dict)

def getImage(filename):
    im = Image.open(filename)
    data = io.BytesIO()
    im.save(data, "PNG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data

@blueprint.route('/uploaderml', methods = ['GET', 'POST'])
@login_required
def uploaderml():
    print(request.method)
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        df = pd.read_csv (f.filename)
        model = request.form['model']
        model_name = request.form['model_name']
        target = request.form['target']
        my_dict = {"Binary Classification": "tab1", "Multiclass Classification": "tab2", "Clustering": "tab3", "Anomaly Detection": "tab4", "Regression": "tab5", "Time Series Forecasting": "tab6"} 
        #diabetes = get_data('diabetes')
        idx=0
        for name, attr in my_dict.items():
            if name==model and idx==0: #Binary Classification
                from pycaret.classification import ClassificationExperiment
                exp = ClassificationExperiment()
                exp.setup(df, target = target, session_id = 123)
                break
            
            idx+=1
        best = exp.compare_models()
        t=exp.pull()
        t.to_csv('./compare_models.csv')
        # plot confusion matrix
        save_file=exp.plot_model(best, plot = 'confusion_matrix',save=True)
        mat_conf = getImage(save_file)
        # plot AUC
        auc = exp.plot_model(best, plot = 'auc',save=True)
        auc = getImage(auc)
        # plot feature importance
        importance = exp.plot_model(best, plot = 'feature',save=True)
        importance = getImage(importance)
        #evaluate_model(best)
        
        # predict on test set
        holdout_pred = exp.predict_model(best)
        # show predictions df
        #holdout_pred.head()
        
        # copy data and drop Class variable
        new_data = df.copy()
        new_data.drop(target, axis=1, inplace=True)
        #new_data.head()

        # predict model on new_data
        prediction= exp.predict_model(best, data = new_data)
        prediction.head()

        # save pipeline
        if not model_name:
            model_name='my_classification_model'
        
        filename='{}'.format(model_name)
        exp.save_model(best, filename)

        return render_template('tools/mlmodel.html',tables=[df.describe().to_html(classes='data')], titles=df.columns.values,my_dict=my_dict,selected_model=model,
        best_data=[t.to_html(classes='data')],best_title = t.columns.values,
        conf_mat_img=mat_conf.decode('utf-8'),
        auc_img=auc.decode('utf-8'),
        imp_img = importance.decode('utf-8'),
        holdout_pred_data=[holdout_pred.describe().to_html(classes='data')],holdout_pred_title = holdout_pred.columns.values,
        prediction_data=[prediction.describe().to_html(classes='data')],prediction_title = prediction.columns.values,
        model_name=model_name,
        target=target,
        msg = "Model has already generated, you can download the model")
        
@blueprint.route('/downloadml', methods = ['GET', 'POST'])
@login_required
def downloadml():
    if request.method == 'POST':
        filename = request.form['model_name']
        filename = '../{}.pkl'.format(filename)
    
    return send_file(filename, 
        download_name=filename, as_attachment=True)


@blueprint.route('/upload_datatest', methods = ['GET', 'POST'])
@login_required
def upload_datatest():
    if request.method=='POST':
        f = request.files['datatest']
        f.save(f.filename)
        df = pd.read_csv(f.filename)
        return render_template('tools/predictme.html',tables=[df.to_html(classes='data')], titles=df.columns.values,filename=f.filename)

@blueprint.route('/uploadmodel', methods = ['GET', 'POST'])
@login_required
def uploadmodel():
    result=''
    if request.method=='POST':
        file=request.form['filedatauji']
        filename = file
        print(filename)
        file='{}'.format(file)

        df = pd.read_csv(file)

        f = request.files['file']
        f.save(f.filename)
        model_name = f.filename.replace('.pkl','')
        
        model = load_model(model_name)
        
        target=request.form['target']

        new_data = df.copy()
        new_data.drop(target, axis=1, inplace=True)

        prediction = predict_model(model,data=new_data,round=0)
        print(prediction.columns)

        prediction_label = prediction['prediction_label']
        prediction_score = prediction['prediction_score']
        
        return render_template('tools/predictme.html',
            tables=[df.to_html(classes='data')], titles=df.columns.values,filename=filename,
            prediction_data=[prediction.to_html(classes='data')],prediction_title=prediction.columns.values)

@blueprint.route('/predictme', methods = ['GET', 'POST'])
@login_required
def predictme():
    return render_template('tools/predictme.html')

# Errors

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

