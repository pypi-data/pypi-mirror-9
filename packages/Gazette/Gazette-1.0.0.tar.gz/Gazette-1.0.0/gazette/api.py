from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os

import bottle
import jsonpickle

from gazette import __version__
from gazette.content_types import all_content_types
from gazette.models import Content


app = bottle.Bottle()

@app.get('/')
def index():
    return {'welcome': 'This is the Gazette API',
            'version': __version__}


@app.get('/content/<full_name:path>')
def get_content(full_name):
    bottle.response.content_type = 'application/json'
    c = Content.get_by_fullname(full_name)
    if c:
        return jsonpickle.dumps(c, unpicklable=False)
    else:
        bottle.abort(404, 'Content not found {}'.format(full_name))


@app.put('/content/<full_name:path>')
def put_content(full_name):
    bottle.response.content_type = 'application/json'

    if not (bottle.request.content_type == 'application/json'
            or bottle.request.content_type.startswith('application/json;')):
        # if the request coming in is not application/json, then bottle won't parse the input into JSON for us
        bottle.abort(415)
    if not bottle.request.json:
        bottle.abort(400)

    c = Content.get_by_fullname(full_name)
    if c:
        c.data = bottle.request.json
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
        item = Type(item_name, data=bottle.request.json)
        item.save()
        bottle.abort(201)  # created


@app.get('/types')
def get_types():
    bottle.response.content_type = 'application/json'
    return {
        'types': sorted(all_content_types().keys()),
    }


# TODO: schema validation, and validation api


@app.error(404)
#@app.error(500)  # conflicts with debug mode
def error(error):
    bottle.response.content_type = 'application/json'
    return json.dumps({'error': error._status_code, 'message': error.body})


"""
# TODO: need a way to find content types
# could iterate subclasses, but would need to ensure custom subclasses were imported
@app.get('/type/<type_name>')
def content_type(type_name):
    return {}
"""


# FIXME: this works for running bottle from the command line, but it's not good to run stuff at import-time
# automatically.  Need to push it into the app initialization.

if os.environ.get('GZ_DS_DIR'):
    from gazette.utils import datastore_json_files
    Content.ds = datastore_json_files(os.environ['GZ_DS_DIR'])
