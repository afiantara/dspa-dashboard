from . import blueprint
from flask import render_template
from flask_login import login_required
from dash_app import individual, industrial

@blueprint.route('/app1')
@login_required
def app1():
    return render_template('dash_app/individual.html', dash_url = individual.url_base)

@blueprint.route('/app2')
@login_required
def app2():
    return render_template('dash_app/industrial.html', dash_url = industrial.url_base)