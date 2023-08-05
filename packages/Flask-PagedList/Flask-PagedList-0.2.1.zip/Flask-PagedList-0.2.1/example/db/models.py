# -*- coding: utf-8 -*-
from . import db


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200))
    composer = db.Column(db.Unicode(220))
    duration = db.Column(db.Integer)
    size = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(precision=10, scale=2))
