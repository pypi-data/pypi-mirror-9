from datetime import datetime
import json
import logging
from pytest_plugin.custom_exceptions import ItemNotStarted
import requests
from requests.exceptions import HTTPError, ConnectionError


__author__ = 'kiryl_zayets'

get_time = lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


class RP_API:
    HEADER = {'Content-Type': 'application/json; charset=utf8'}
    HOST = 'https://evbyminsd7776.minsk.epam.com:8443/reportportal-ws/api/v1'
    # HOST = 'https://rp.epam.com/reportportal-ws'
    USER = 'default'
    PASSWORD = '1q2w3e'

    START_LAUNCH = '/{project_name}/launch'
    FINISH_LAUNCH = '/{project_name}/launch/{launch_id}/finish'
    START_ROOT = '/{project_name}/item'
    START_ITEM = '/{project_name}/item/{item_id}'
    FINISH_ITEM = '/{project_name}/item/{item_id}'
    LOG = '/{project_name}/log'


class ErpActions(object):
    auth = (RP_API.USER, RP_API.PASSWORD)
    proj, suite_id, launch_id = None, None, None
    request = {'POST': requests.post, 'PUT': requests.put, 'GET': requests.get, 'DELETE': requests.delete}
    LOGGER = logging.getLogger(__name__)

    @classmethod
    def prepare_json(cls, command=RP_API.START_ROOT, http='POST', query_string=None, **kwargs):
        from pytest_plugin.mapping_fixture_action import ItemState

        keys_values = kwargs
        if query_string is None:
            query_string = {}
        try:
            query_string['project_name'] = ItemState.project_name
            if not keys_values.get('end_time') and not  keys_values.get('time'):
                keys_values['start_time'] = get_time()
            if keys_values.get('type') in ['LAUNCH', 'LOG']:
                keys_values.pop('launch_id', None)
                keys_values.pop('type', None)
            req = RP_API.HOST + command.format(**query_string)
            data = json.dumps(keys_values)
            http_action = cls.request[http]
        except KeyError:
            cls.LOGGER.error('No action is found', exc_info=True)


        def send():
            try:
                response = http_action(req, data=data, auth=cls.auth, headers=RP_API.HEADER, verify=False)
            except (HTTPError, ConnectionError) as e:
                cls.LOGGER.error('Connection is lost. Trying to reconnect.', exc_info=True)
                response = None
                while not response:
                    try:
                        response = http_action(req, data=data, auth=cls.auth, headers=RP_API.HEADER, verify=False)
                    except (HTTPError, ConnectionError):
                        cls.LOGGER.error('Reconnect...')
                else:
                    return json.loads(response.content.decode())
            else:
                try:
                    return json.loads(response.content.decode())
                except KeyError as e:
                    if response.status_code is 200:
                        return
                    else:
                        cls.LOGGER.error('Key" id" is not found in response! Respons is {}'.
                                         format(str(response.content)), exc_info=True)
        return send


    @classmethod
    def start(cls, item, query_s=None):
        from pytest_plugin.mapping_fixture_action import ItemState

        query_string = None
        unique = {'LAUNCH': RP_API.START_LAUNCH, 'SUITE': RP_API.START_ROOT}
        url = unique.get(item.type, RP_API.START_ITEM)
        if item.type not in ['LAUNCH', 'SUITE', 'BEFORE_SUITE'] and not query_string and item.type.find('AFTER_')==-1:
            query_string = {'item_id': ItemState.active_item_id}
        else:
            query_string = query_s

        response = cls.prepare_json(command=url, http='POST', name=item.name, launch_id=cls.launch_id, type=item.type,
                                    description=item.desc, query_string=query_string)()
        try:
            item.id = response['id']
        except KeyError:
            cls.LOGGER.error('Item {} start failure: response "{}"!'.format(item.name, response))
            raise ItemNotStarted('Item {} start failure: response "{}"!'.format(item.name, response))
        else:
            if item.type is 'LAUNCH':
                cls.launch_id = item.id
            return item.id

    @classmethod
    def finish(cls, id, status='PASSED', type='ITEM'):
        if type is 'LAUNCH':
            query_string = {'launch_id': cls.launch_id}
            command = RP_API.FINISH_LAUNCH
        else:
            query_string = {'item_id': id}
            command = RP_API.FINISH_ITEM
        msg = cls.prepare_json(command=command, http='PUT', query_string=query_string, status=status,
                               end_time=get_time())()
        if msg:
            message = msg.get('error_code', None)
            if message:
                cls.LOGGER.error('Item close error! ERROR_CODE is {error_code}, MESSAGE is {message}'.format(**msg))
                # raise ItemNotClosed('Item close error! ERROR_CODE is {error_code}, MESSAGE is {message}'.format(**msg))

    @classmethod
    def fixture(cls, item):
        from pytest_plugin.mapping_fixture_action import ItemState

        if item.fixture.scope is 'session':
            if not ItemState.current_session:
                ItemState.current_session = ItemState('Global events', 'Holder for global objects',
                                                      type='SUITE').activate().id

        send_to = {'session': [ItemState.current_session, 'BEFORE_SUITE'],
                   'module': [ItemState.current_module.id, 'BEFORE_SUITE'],
                   'class': [ItemState.active_item_id, 'BEFORE_CLASS'],
                   'function': [ItemState.active_item_id, 'BEFORE_METHOD']}

        item.type = send_to[item.fixture.scope][1]
        cls.start(item, query_s={'item_id': send_to[item.fixture.scope][0]})


    @classmethod
    def start_teardown_fixture(cls, item):
        from pytest_plugin.mapping_fixture_action import ItemState

        send_to = {'session': [ItemState.current_session, 'AFTER_SUITE'],
                   'module': [ItemState.active_item_id, 'AFTER_TEST'],
                   'class': [ItemState.active_item_id, 'AFTER_CLASS'],
                   'function': [ItemState.active_item_id, 'AFTER_METHOD']}
        item.type = send_to[item.fixture.scope][1]
        cls.start(item, query_s={'item_id': send_to[item.fixture.scope][0]})

    @classmethod
    def send_log(cls):
        cls.prepare_json(command=RP_API.LOG, http='POST', type='LOG', item_id=item.id, message=full_sign, level=level, time=get_time())()


    @classmethod
    def log(cls, item):
        item.type = 'LOG'
        level = ''
        if item.failed:
            trace = '\n'.join([line for entry in item.stderr.reprtraceback.reprentries for line in entry.lines])
            message = 'Line = {crash.lineno} Message = {crash.message} Path = {crash.path}\n'.format(crash = item.stderr.reprcrash)
            full_sign = '{message} \n {stacktrace}'.format(message=message, stacktrace = trace)
            level = 'ERROR'
            cls.prepare_json(command=RP_API.LOG, http='POST', type=item.type, item_id=item.id, message=full_sign, level=level, time=get_time())()
        elif not item.failed:
            rows = str(item.stdout).split('\\n')
            for row in rows:
                if row.find('ERROR') > 0:
                    level = 'ERROR'
                else:
                    level = 'INFO'
                cls.prepare_json(command=RP_API.LOG, http='POST', type=item.type, item_id=item.id, message=row, level=level, time=get_time())()

