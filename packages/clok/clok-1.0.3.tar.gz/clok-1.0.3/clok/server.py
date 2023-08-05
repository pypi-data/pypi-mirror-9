#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Clok

Usage:
  clok [-a ADDRESS -p PORT --database FILE --log LOG]
  clok -h | --help
  clok -v | --version

Options:
  -h --help             Show this screen.
  -v --version          Show version.
  -d --database FILE    Specify the database filename (JSON storage).
                        [default: ./db.json]
  -a --address ADDRESS  Specify on which address to listen.
                        [default: 0.0.0.0]
  -p --port PORT        Specify on which port to listen.
                        [default: 8000]
  --log LOG             Specify where to log messages, and which level to set.
                        Can be "stderr", "syslog", or a filename, followed by the level.
                        [default: stderr:INFO]

"""

from __future__ import unicode_literals, absolute_import

from os.path import dirname, abspath, join
from functools import wraps
import json

from bottle import Bottle, view, request, TEMPLATE_PATH, static_file
from docopt import docopt
from tinydb import TinyDB, where

from . import __version__ as VERSION
from .radio import Radio
from .cron import CronService
from .log import Logger
from .models import (
    setup_db, Alarm, NoAlarms, Webradio, AttributeRequired
)

app = Bottle()
HERE = abspath(dirname(__file__))


# ~~~ UTILS ~~~

def update_cron_after(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        app.cron.update()
        return ret
    return wrapper


def find_data_in(req):
    if req.forms and '__json_data' in req.forms:
        return json.loads(req.forms['__json_data'])
    return req.json or req.forms


# ~~~ Static Routes ~~~

@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root=join(HERE, 'static', "js"))


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root=join(HERE, 'static', "css"))


@app.get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root=join(HERE, 'static', "img"))


@app.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return static_file(filename, root=join(HERE, 'static', "fonts"))


# ~~~ VIEWS ~~~

@app.route('/')
@view('index')
def index():
    return {'url': app.radio.url, 'playing': app.radio.is_playing}


# ~~~ API ~~~

def APIResponse(status, **kwargs):
    dico = kwargs
    dico["status"] = status
    return dico


@app.get('/api/play/')
@app.get('/api/play/<url:path>')
def api_play(url=None):
    app.radio.play(url)
    return APIResponse('success')


@app.get('/api/stop/')
def api_stop():
    app.radio.stop()
    return APIResponse('success')


@app.get('/api/togglepause/')
def api_togglepause():
    app.radio.togglepause()
    return APIResponse('success')


@app.get('/api/infos/')
def api_infos():
    infos = {
        'url': app.radio.url,
        'playing': app.radio.is_playing,
    }
    return APIResponse('success', infos=infos)


@app.get('/api/update/')
@update_cron_after
def api_update():
    return APIResponse('success')


# Webradios

@app.get('/api/webradios/')
def api_list_webradios():
    return APIResponse('success', webradios=Webradio.all(to_dict=True))


@app.get('/api/webradios/<uuid>')
def api_get_webradio(uuid):
    found = Webradio.get(uuid=uuid)
    if found is None:
        return APIResponse('notfound')
    return APIResponse('success', webradio=found.to_dict())


@app.post('/api/webradios/')
def api_add_webradio():
    data = find_data_in(request)
    try:
        r = Webradio(**data).save()
    except AttributeRequired:
        return APIResponse('attributerequired', details=Webradio.required_fields())
    return APIResponse('success', webradio=r.to_dict())


@app.delete('/api/webradios/<uuid>')
@update_cron_after
def api_remove_webradio(uuid):
    Webradio.remove(where('uuid') == uuid)
    Alarm.remove(where('webradio') == uuid)
    return APIResponse('success')


@app.put('/api/webradios/<uuid>')
@update_cron_after
def api_edit_webradio(uuid):
    in_db = Webradio.get(uuid=uuid)
    if in_db is None:
        return APIResponse('notfound')

    data = find_data_in(request)
    for k, v in data.items():
        setattr(in_db, k, v)
    in_db.save()
    return APIResponse('success', webradio=in_db.to_dict())


# Alarms

@app.get('/api/alarms/')
def api_list_alarms():
    return APIResponse('success', alarms=Alarm.all(to_dict=True))


@app.get('/api/alarms/<uuid>')
def api_get_alarm(uuid):
    found = Alarm.get(uuid=uuid)
    if found is None:
        return APIResponse('notfound')
    return APIResponse('success', alarm=found.to_dict())


@app.post('/api/alarms/')
@update_cron_after
def api_add_alarm():
    data = find_data_in(request)
    try:
        r = Alarm(**data).save()
    except AttributeRequired:
        return APIResponse('attributerequired', details=Alarm.required_fields())
    return APIResponse('success', alarm=r.to_dict())


@app.delete('/api/alarms/<uuid>')
@update_cron_after
def api_remove_alarm(uuid):
    Alarm.remove(where('uuid') == uuid)
    return APIResponse('success')


@app.put('/api/alarms/<uuid>')
@update_cron_after
def api_edit_alarm(uuid):
    in_db = Alarm.get(uuid=uuid)
    if in_db is None:
        return APIResponse('notfound')

    data = find_data_in(request)
    for k, v in data.items():
        setattr(in_db, k, v)
    in_db.save()
    return APIResponse('success', alarm=in_db.to_dict())


@app.get('/api/next_event/')
def api_next_event():
    try:
        event = Alarm.next_event_overall()
    except NoAlarms:
        return APIResponse('success')
    event = {
        'time': event.time.isoformat(),
        'alarm': event.alarm.to_dict(),
        'type': event.type,
    }
    return APIResponse('success', event=event)


# ~~~ MAIN ~~~

def main():
    args = docopt(__doc__, version='clok ' + VERSION)

    HOST = args['--address']
    PORT = int(args['--port'])
    DBFILE = args['--database']
    LOG_ARG, LOG_LVL = args['--log'].rsplit(':', 1)
    if LOG_ARG not in ('stderr', 'syslog'):
        LOG_SETUP = dict(type='file', filename=LOG_ARG, level=LOG_LVL)
    else:
        LOG_SETUP = dict(type=LOG_ARG, level=LOG_LVL)
    TEMPLATE_PATH.append(join(HERE, 'views'))

    app.logger = Logger('clok')
    app.logger.setup(**LOG_SETUP)
    app.radio = Radio()
    db = TinyDB(DBFILE)
    setup_db(db)  # setup database for this process (main process)
    app.cron = CronService(log_setup=LOG_SETUP)
    app.cron.update()
    try:
        app.run(host=HOST, port=PORT, server='waitress')
    except KeyboardInterrupt:
        app.radio.kill()


if __name__ == '__main__':
    main()
