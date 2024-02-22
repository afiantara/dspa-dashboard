import json
import os
import pandas as pd
import requests
import urllib

from bs4 import BeautifulSoup
from flask import render_template, request
from logging import getLogger

from dtale.app import build_app, get_instance
from dtale.global_state import cleanup
from dtale.views import startup

def update_dtale_data(df):
    cleanup("1")
    # load data to D-Tale
    startup(data_id="1", data=df)
'''
def build_chart_url(names):
    params = {
        "chart_type": "line",
        "x": "Season",
        "y": json.dumps(["HR"]),
        "group": json.dumps(["name"]),
        "group_val": json.dumps([{"name": name} for name in names]),
    }
    return "/dtale/charts/1?{}".format(urllib.parse.urlencode(params))
'''

def load_data_props():
    instance = get_instance("1")

    if instance is not None:
        #names = instance.data["name"].unique()
        #chart_url = build_chart_url(names)
        return dict(
            #names=", ".join(instance.data["name"].unique()),
            data_exists=True,
            #chart_url=chart_url,
        )
    return dict(data_exists=False)


if __name__ == "__main__":
    # this will allow you to load templates from you local directory as well as the D-Tale templates
    additional_templates = os.path.join(os.path.dirname(__file__), "templates")
    
    app = build_app(reaper_on=False, additional_templates=additional_templates)

    @app.route("/")
    def base():
        cleanup("1") # clean up data
        return render_template("home.html", **load_data_props())

    @app.route("/upload-data",methods = ['GET', 'POST'])
    def upload_data():
        if request.method == 'POST':
            f = request.files['file']
            f.save(f.filename)
            df = pd.read_csv (f.filename)
            update_dtale_data(df)
        
        return render_template(
            "home.html",
            **load_data_props()
        )
        
    app.run(host="0.0.0.0", port=9000, debug=True)