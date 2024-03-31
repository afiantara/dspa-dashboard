# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit

from apps.config import config_dict
from apps import create_app, db
# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)

Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

if __name__ == "__main__":
    '''
    from werkzeug.middleware.dispatcher import DispatcherMiddleware # use to combine each Flask app into a larger one that is dispatched based on prefix
    from werkzeug.serving import run_simple # werkzeug development server
    from dtaleapp.main import app as flask_dtale
    application = DispatcherMiddleware(app, {'/1': flask_dtale})
    run_simple('localhost', 8080, application, use_reloader=True, use_debugger=True, use_evalex=True)
    #app.run(host="0.0.0.0", port=8080)
    '''
    app.run(host='0.0.0.0')
