# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Agus Afiantara
"""

from flask import Blueprint

blueprint = Blueprint(
    'dash_app_blueprint',
    __name__,
    url_prefix=''
)
