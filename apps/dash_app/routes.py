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
    from libs.map_industrial import do_map
    iframe = do_map()
    return render_template('dash_app/industrial.html', dash_url = industrial.url_base,iframe=iframe)