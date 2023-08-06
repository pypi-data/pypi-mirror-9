from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os

import bottle
import jsonpickle

from gazette import __version__
from gazette.content_types import all_content_types
from gazette.models import Content, content_full_name
from gazette.utils import jsonpickle_date, datetime_to_json


app = bottle.Bottle()

@app.get('/')
def index():
    return {'welcome': 'This is the Gazette API',
            'version': __version__}


@app.get('/content/<full_name:path>')
def get_content(full_name):
    bottle.response.content_type = 'application/json'
    if full_name.endswith('/all'):
        return get_versions(full_name[:-len('/all')])

    c = Content.get_by_fullname(full_name)
    if c:
        with jsonpickle_date():
            return jsonpickle.dumps(c, unpicklable=False)
    else:
        bottle.abort(404, 'Content not found {}'.format(full_name))


def get_versions(full_name):
    c = Content.get_by_fullname(full_name)
    if not c:
        bottle.abort(404, 'Content not found {}'.format(full_name))
    return {
        'versions': [
            {'version': v.version,
             'timestamp': datetime_to_json(v.timestamp),
             'url': content_full_name(v, version=True),
             'author': v.author,
             } for v in c.versions()
        ]
    }


def check_input_is_json(req):
    if not (req.content_type == 'application/json'
            or req.content_type.startswith('application/json;')):
        # if the request coming in is not application/json, then bottle won't parse the input into JSON for us
        bottle.abort(415)
    if not req.json:
        bottle.abort(400)


@app.put('/content/<full_name:path>')
def put_content(full_name):
    bottle.response.content_type = 'application/json'
    check_input_is_json(bottle.request)
    data = bottle.request.json
    author = data.pop('gazette.author', None)

    c = Content.get_by_fullname(full_name)
    if c:
        c.data = data
        c.author = author
        c.save()
    else:
        try:
            type_name, item_name = full_name.split('/', 1)
        except ValueError:
            bottle.abort(404)
        try:
            Type = all_content_types()[type_name]
        except KeyError:
            bottle.abort(404)
        item = Type(item_name, data=data, author=author)
        item.save()
        bottle.abort(201)  # created


@app.get('/types')
def get_types():
    bottle.response.content_type = 'application/json'
    return {
        'types': sorted(all_content_types().keys()),
    }


@app.put('/preview/<content_type>')
def preview(content_type):
    bottle.response.content_type = 'text/html'
    check_input_is_json(bottle.request)
    try:
        Type = all_content_types()[content_type]
    except KeyError:
        bottle.abort(404)
    else:
        item = Type('preview', data=bottle.request.json)
        return item._render_html()


@app.error(404)
#@app.error(500)  # conflicts with debug mode
def error(error):
    bottle.response.content_type = 'application/json'
    return json.dumps({'error': error._status_code, 'message': error.body})


# FIXME: this works for running bottle from the command line, but it's not good to run stuff at import-time
# automatically.  Need to push it into the app initialization.

if os.environ.get('GZ_DS_DIR'):
    from gazette.utils import datastore_json_files
    Content.ds = datastore_json_files(os.environ['GZ_DS_DIR'])
