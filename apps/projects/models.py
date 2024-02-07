# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Agus Afiantara
"""


from apps import db
from flask_login import UserMixin

class UpdateProgress(db.Model, UserMixin):

    __tablename__ = 'ProgressProject'
    code_project = db.Column(db.String, primary_key=True)
    tgl_update = db.Column(db.DateTime)
    plan_project = db.Column(db.Numeric)
    real_project = db.Column(db.Numeric)
    notes = db.Column(db.String)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.code_project)

class UpdateProgressHist(db.Model, UserMixin):

    __tablename__ = 'ProgressProjectHist'
    
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    code_project = db.Column(db.String)
    tgl_update= db.Column(db.DateTime)
    plan_project = db.Column(db.Numeric)
    real_project = db.Column(db.Numeric)
    notes = db.Column(db.String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.code_project)

class Projects(db.Model, UserMixin):

    __tablename__ = 'Projects'
    
    id_project = db.Column(db.Integer, primary_key=True,autoincrement=True)
    code_project = db.Column(db.String)
    desc_project= db.Column(db.String)
    jenis_kegiatan = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    year_project = db.Column(db.Numeric)
    plan_project = db.Column(db.Numeric)
    real_project = db.Column(db.Numeric)
    performance = db.Column(db.Numeric)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.code_project)

def project_loader(code_project):
    print('project_loader')
    return UpdateProgress.query.filter_by(code_project=code_project).first()


def request_loader(request):
    code_project = request.form.get('code_project')
    print(f"request_loader: ",code_project)
    progress = UpdateProgress.query.filter_by(code_project=code_project).first()
    return progress if progress else None
