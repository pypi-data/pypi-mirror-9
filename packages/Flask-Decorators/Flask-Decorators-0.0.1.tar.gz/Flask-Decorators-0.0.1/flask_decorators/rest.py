from functools import wraps
import json
from flask import request, current_app, make_response, render_template


def render_html(template, **kwargs):
    """Return a rendered html

    Usage:

    .. code::py

        @app.route('/')
        def index():
            return render_html('index.html', name='World')
    """
    return render_template(template, **kwargs)


def render_json(result, defaults):
    def _(*args, **kwargs):
        json_string = json.dumps(result)
        return current_app.response_class(response=json_string, mimetype='application/json')
    return _


def restful_render(func):
    header = request.headers['']
    header     # TODO: Choose renderer by header
    render = render_html

    @wraps(func)
    def _(*args, **kwargs):
        return render(**kwargs)
    return _
