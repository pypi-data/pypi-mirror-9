# -*- coding: utf-8 -*-
from flask import render_template
from flask import request
from flask.ext.classy import FlaskView
from werkzeug.exceptions import abort

import pagedlist

from ..db import models

PAGE_SIZE = 10


class UnobtrusiveView(FlaskView):
    route_base = '/unobtrusive'

    def index(self):
        page = request.args.get('page', None)
        if page is not None and page < 1:
            abort(404)
        page = int(page or 1)
        query = models.Track.query
        paged_list = pagedlist.PagedList(query, page or 1, PAGE_SIZE)

        if request.is_xhr:
            return render_template('unobtrusive/_partial.html', paged_list=paged_list)
        else:
            return render_template('unobtrusive/index.html', paged_list=paged_list)
