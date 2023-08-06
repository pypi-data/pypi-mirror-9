import json
import datetime
import requests
import pytz
import re

from datetime import timedelta
from functools import wraps
from flask import make_response, request, current_app
from functools import update_wrapper

from alerta.app import app, db
from alerta.app.metrics import Timer
from alerta.plugins import load_plugins, RejectException

LOG = app.logger

plugins = load_plugins()

duplicate_timer = Timer('alerts', 'duplicate', 'Duplicate alerts', 'Total time to process number of duplicate alerts')
correlate_timer = Timer('alerts', 'correlate', 'Correlated alerts', 'Total time to process number of correlated alerts')
create_timer = Timer('alerts', 'create', 'Newly created alerts', 'Total time to process number of new alerts')


class DateEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S') + ".%03dZ" % (obj.microsecond // 1000)
        else:
            return json.JSONEncoder.default(self, obj)


# Over-ride jsonify to support Date Encoding
def jsonify(*args, **kwargs):
    return current_app.response_class(json.dumps(dict(*args, **kwargs), cls=DateEncoder,
                                                 indent=None if request.is_xhr else 2), mimetype='application/json')


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated


PARAMS_EXCLUDE = [
    '_',
    'callback',
    'token',
    'api-key'
]


def parse_fields(r):

    query_time = datetime.datetime.utcnow()

    params = r.args.copy()

    for s in PARAMS_EXCLUDE:
        if s in params:
            del params[s]

    if params.get('q', None):
        query = json.loads(params['q'])
        del params['q']
    else:
        query = dict()

    page = params.get('page', 1)
    if 'page' in params:
        del params['page']
    page = int(page)

    if params.get('from-date', None):
        try:
            from_date = datetime.datetime.strptime(params['from-date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError, e:
            LOG.warning('Could not parse from-date query parameter: %s', e)
            raise
        from_date = from_date.replace(tzinfo=pytz.utc)
        del params['from-date']
    else:
        from_date = None

    if params.get('to-date', None):
        try:
            to_date = datetime.datetime.strptime(params['to-date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError, e:
            LOG.warning('Could not parse to-date query parameter: %s', e)
            raise
        to_date = to_date.replace(tzinfo=pytz.utc)
        del params['to-date']
    else:
        to_date = query_time
        to_date = to_date.replace(tzinfo=pytz.utc)

    if from_date and to_date:
        query['lastReceiveTime'] = {'$gt': from_date, '$lte': to_date}
    elif to_date:
        query['lastReceiveTime'] = {'$lte': to_date}

    if params.get('duplicateCount', None):
        query['duplicateCount'] = int(params.get('duplicateCount'))
        del params['duplicateCount']

    if params.get('repeat', None):
        query['repeat'] = True if params.get('repeat', 'true') == 'true' else False
        del params['repeat']

    sort = list()
    direction = 1
    if params.get('reverse', None):
        direction = -1
        del params['reverse']
    if params.get('sort-by', None):
        for sort_by in params.getlist('sort-by'):
            if sort_by in ['createTime', 'receiveTime', 'lastReceiveTime']:
                sort.append((sort_by, -direction))  # reverse chronological
            else:
                sort.append((sort_by, direction))
        del params['sort-by']
    else:
        sort.append(('lastReceiveTime', -direction))

    group = list()
    if 'group-by' in params:
        group = params.get('group-by')
        del params['group-by']

    if 'limit' in params:
        limit = params.get('limit')
        del params['limit']
    else:
        limit = app.config['QUERY_LIMIT']
    limit = int(limit)

    ids = params.getlist('id')
    if len(ids) == 1:
        query['$or'] = [{'_id': {'$regex': '^' + ids[0]}}, {'lastReceiveId': {'$regex': '^' + ids[0]}}]
        del params['id']
    elif ids:
        query['$or'] = [{'_id': {'$regex': re.compile('|'.join(['^' + i for i in ids]))}}, {'lastReceiveId': {'$regex': re.compile('|'.join(['^' + i for i in ids]))}}]
        del params['id']

    for field in params:
        value = params.getlist(field)
        if len(value) == 1:
            value = value[0]
            if field.endswith('!'):
                if value.startswith('~'):
                    query[field[:-1]] = dict()
                    query[field[:-1]]['$not'] = re.compile(value[1:], re.IGNORECASE)
                else:
                    query[field[:-1]] = dict()
                    query[field[:-1]]['$ne'] = value
            else:
                if value.startswith('~'):
                    query[field] = dict()
                    query[field]['$regex'] = re.compile(value[1:], re.IGNORECASE)
                else:
                    query[field] = value
        else:
            if field.endswith('!'):
                if '~' in [v[0] for v in value]:
                    value = '|'.join([v.lstrip('~') for v in value])
                    query[field[:-1]] = dict()
                    query[field[:-1]]['$not'] = re.compile(value, re.IGNORECASE)
                else:
                    query[field[:-1]] = dict()
                    query[field[:-1]]['$nin'] = value
            else:
                if '~' in [v[0] for v in value]:
                    value = '|'.join([v.lstrip('~') for v in value])
                    query[field] = dict()
                    query[field]['$regex'] = re.compile(value, re.IGNORECASE)
                else:
                    query[field] = dict()
                    query[field]['$in'] = value

    return query, sort, group, page, limit, query_time


def process_alert(incomingAlert):

    for plugin in plugins:
        try:
            incomingAlert = plugin.pre_receive(incomingAlert)
        except RejectException:
            raise
        except Exception as e:
            raise RuntimeError('Error while running pre-receive plug-in: %s' % str(e))
        if not incomingAlert:
            raise SyntaxError('Plug-in pre-receive hook did not return modified alert')

    try:
        if db.is_duplicate(incomingAlert):
            started = duplicate_timer.start_timer()
            alert = db.save_duplicate(incomingAlert)
            duplicate_timer.stop_timer(started)
        elif db.is_correlated(incomingAlert):
            started = correlate_timer.start_timer()
            alert = db.save_correlated(incomingAlert)
            correlate_timer.stop_timer(started)
        else:
            started = create_timer.start_timer()
            alert = db.create_alert(incomingAlert)
            create_timer.stop_timer(started)
    except Exception as e:
        raise RuntimeError(e)

    for plugin in plugins:
        try:
            plugin.post_receive(alert)
        except Exception as e:
            raise RuntimeError('Error while running post-receive plug-in: %s' % str(e))

    return alert
