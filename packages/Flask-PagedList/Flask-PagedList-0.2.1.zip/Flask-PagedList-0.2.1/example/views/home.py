# -*- coding: utf-8 -*-
from flask import render_template
from flask import request
from flask.ext.classy import FlaskView
from werkzeug.exceptions import abort

import pagedlist

from ..db import models

PAGE_SIZE = 10


class HomeView(FlaskView):
    route_base = '/'

    def index(self):
        page = request.args.get('page', None)
        if page is not None and page < 1:
            abort(404)
        page = int(page or 1)
        query = models.Track.query
        paged_list = pagedlist.PagedList(query, page or 1, PAGE_SIZE)
        return render_template('home/index.html', paged_list=paged_list)
