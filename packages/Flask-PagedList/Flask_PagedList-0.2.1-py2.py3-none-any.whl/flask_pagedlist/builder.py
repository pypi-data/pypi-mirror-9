import jinja2
from flask import url_for

from pagedlist.web import builder as pl_builder


class Builder(object):
    @classmethod
    def paged_list_pager(cls, paged_list, page_url_generator, options=None):
        return jinja2.Markup(pl_builder.Builder.paged_list_pager(
            paged_list, page_url_generator, options))

    @classmethod
    def paged_list_goto_page_form(cls, paged_list, form_action, options=None):
        return jinja2.Markup(pl_builder.Builder.paged_list_goto_page_form(
            paged_list, form_action, options))

    @classmethod
    def page_url_generator(cls, endpoint):
        return lambda page: url_for(endpoint, page=page)
