# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask import render_template, redirect, request, url_for
from apps import db
from apps.projects import blueprint
from apps.projects.forms import UpdateProgressForm,ProjectForm
from flask_login import login_required
from datetime import datetime
from apps.projects.models import UpdateProgress,UpdateProgressHist,Projects

@blueprint.route('/')
@login_required
def route_default():
    print('projects_blueprint.route(/)')
    return redirect(url_for('projects_blueprint.show'))


@blueprint.route('/delete_proyek/<int:proyekid>', methods=['GET'])
@login_required
def delete_proyek(proyekid):
    project = Projects.query.get(proyekid)
    db.session.delete(project)
    db.session.commit()
    print(f'projects_blueprint.delete_proyek',proyekid)
    return redirect(url_for('projects_blueprint.master_proyek'))

@blueprint.route('/master_proyek')
@login_required
def master_proyek():
    print('projects_blueprint.master_proyek')
    proyeks = getListProyek()
    return render_template('project/master_proyek.html',datetime = str(datetime.now()),proyek=proyeks)

# Project handling
@blueprint.route('/show', methods=['GET', 'POST'])
@login_required
def show():
    return render_template('project/update_progress.html',datetime = str(datetime.now()))

@blueprint.route('/showregister', methods=['GET', 'POST'])
@login_required
def showregister():
    today = datetime.now()
    year = today.strftime("%Y")
    return render_template('project/register_proyek.html',datetime = str(datetime.now()),rkat=['RKAT','RUTIN'],tahun=year)

@blueprint.route('/updateprogress', methods=['GET', 'POST'])
@login_required
def updateprogress():
    print('updateprogress')
    project_form = UpdateProgressForm(request.form)
    if 'updateprogress' in request.form:
        kode = request.form['code_project']
        plan = request.form['plan_project']
        realisasi = request.form['real_project']
        notes = request.form['notes']
        tglupdate=request.form['tgl_update']
        
        exp_year  = int(tglupdate[:4])
        exp_month =  int(tglupdate[5:7])
        exp_date = int(tglupdate[8:10])
        exp_date =datetime(exp_year,exp_month,exp_date)

        # Check kode exists
        progress = UpdateProgress.query.filter_by(code_project=kode).first()
        
        if not progress:
            progress = UpdateProgress(**request.form)
            progress.tgl_update=exp_date
            # else we can create the user
            db.session.add(progress)
        else:
            progress.plan_project=plan
            progress.real_project=realisasi
            progress.tgl_update=exp_date

        db.session.commit()

        #insert historical
        progress = UpdateProgressHist(**request.form)
        progress.code_project=kode
        progress.plan_project=plan
        progress.real_project=realisasi
        progress.tgl_update=exp_date
        progress.notes=notes

        db.session.add(progress)

        db.session.commit()


    return render_template('home/index.html')

def getListProyek():
    results = db.session.query(Projects).all()
    for result in results:
        progress = UpdateProgress.query.filter_by(code_project=result.code_project).first()
        if not progress is None:
            result.plan_project = progress.plan_project
            result.real_project = progress.real_project
            result.performance=(result.real_project/result.plan_project)*100
    db.session.commit()

    return results

@blueprint.route('/registerproyek', methods=['GET', 'POST'])
@login_required
def registerproyek():
    print('registerproyek')
    project_form = ProjectForm(request.form)
    if 'registerproyek' in request.form:
        kode = request.form['code_project']
        deskripsi = request.form['desc_project']
        jenis = request.form['jenis_kegiatan']
        year = request.form['year_project']
        mulai= request.form['start_date']
        selesai= request.form['end_date']

        tgl_mulai_year  = int(mulai[:4])
        tgl_mulai_mth =  int(mulai[5:7])
        tgl_mulai_day = int(mulai[8:10])
        tgl_mulai = datetime(tgl_mulai_year,tgl_mulai_mth,tgl_mulai_day)

        tgl_selesai_year  = int(selesai[:4])
        tgl_selesai_mth =  int(selesai[5:7])
        tgl_selesai_day = int(selesai[8:10])
        tgl_selesai = datetime(tgl_selesai_year,tgl_selesai_mth,tgl_selesai_day)

        proyek = Projects.query.filter_by(code_project=kode).first()
        if not proyek:
            proyek = Projects(**request.form)
            proyek.start_date=tgl_mulai
            proyek.end_date=tgl_selesai

            db.session.add(proyek)
        else:
            proyek.jenis_kegiatan=jenis
            proyek.desc_project=deskripsi
            proyek.year_project=year
            proyek.start_date=tgl_mulai
            proyek.end_date=tgl_selesai

        db.session.commit()

    # getlist proyek 
    proyeks =getListProyek()

    return render_template('home/index.html',proyek=proyeks)

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

