# import std libs
import os
from pkg_resources import resource_filename
import json
# import third party libs
import jinja2
# import local libs
from cycle.meta import __title__ as pkgname


def format_json(data):
    return json.dumps(data, indent=2, sort_keys=True)

def load_resource_json(resource_path, pkgname=pkgname):
    chunks = resource_path.split('/')
    return json.load(open(resource_filename(pkgname, os.path.join(*chunks)), 'r'))

def get_template_renderer(template_string=None):
    jinja_tmpl_opts = dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    )
    tmpl_environ = jinja2.Environment(**jinja_tmpl_opts)
    return tmpl_environ.from_string(template_string)
