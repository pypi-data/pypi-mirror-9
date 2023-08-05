# -*- coding: utf-8 -*-
import os
from datetime import timedelta

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.pagedlist import PagedList

from .db import db
from .db import models
from .views.home import HomeView
from .views.unobtrusive import UnobtrusiveView


def custom_jinja2_filters(app):
    @app.template_filter('human_duration')
    def human_duration(millis):
        td = timedelta(milliseconds=millis)
        return str(td)

    @app.template_filter('human_price')
    def human_price(price):
        return '$ {0:.2f}'.format(price)


def create_app():
    app = Flask(__name__)

    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data', 'database.db'
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_path

    # SQLAlchemy
    db.app = app
    db.init_app(app)
    # Register views
    HomeView.register(app)
    UnobtrusiveView.register(app)
    # Bootstrap
    Bootstrap(app)
    # PagedList
    PagedList(app)
    # Helpers
    custom_jinja2_filters(app)
    return app
