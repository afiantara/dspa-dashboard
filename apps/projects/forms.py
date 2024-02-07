# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Agus Afiantara
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import  DataRequired

# projects 

class UpdateProgressForm(FlaskForm):
    code_project = StringField('Kode Kegiatan',
                             id='code_project',
                             validators=[DataRequired()])
    tgl_update = StringField('Tanggal Update',
                             id='tgl_update',
                             validators=[DataRequired()])
    plan = StringField('Plan (%)',
                             id='plan',
                             validators=[DataRequired()])     
    realisasi = StringField('Realisasi (%)',
                             id='realisasi',
                             validators=[DataRequired()])

    notes = StringField('Catatan',
                             id='notes'
                             )


class ProjectForm(FlaskForm):
    code_project = StringField('Kode Kegiatan',
                             id='code_project',
                             validators=[DataRequired()])
    desc_project = StringField('Deskripsi Kegiatan',
                             id='desc_project',
                             validators=[DataRequired()])       
    jenis_kegiatan = StringField('Jenis Kegiatan',
                             id='jenis_kegiatan',
                             validators=[DataRequired()])

    start_date 	= StringField('Tanggal Mulai',
                             id='start_date',
                             validators=[DataRequired()])
	
    end_date	= StringField('Tanggal Selesai',
                             id='end_date',
                             validators=[DataRequired()])

    plan_project = StringField('Plan (%)',
                             id='plan_project'
                             )
    real_project = StringField('Real (%)',
                             id='real_project'
                             )
    performance = StringField('Performance',
                             id='performance'
                             )
    notes = StringField('Catatan',
                             id='notes'
                             )

    year_project= StringField('Tahun Proyek',
                             id='year_project'
                             )