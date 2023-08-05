# -*- coding: utf-8 -*-
"""
pytest_erp
~~~~~~~~~~~~~~~~

py.test plugin to show tests statistics on epam's REST service.

:copyright: (c) 2013-2014 by Kiryl Zayets.

"""
import inspect
import json
import logging
from logging import config, handlers
import os

from _pytest.python import is_generator, getfixturemarker, Generator
import pytest
from pytest_plugin.ext_fixtures_behaviour import ExtSetupState, ExtModule, ExtFunction, ExtClass, ExtFixtureManager
from pytest_plugin.mapping_fixture_action import ItemState
from pytest_plugin.rest_erp_client import ErpActions, RP_API
from pytest_plugin.logger_extension import RestFilter


LOGGER = None


def setup_logging(default_name='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    dir = os.path.dirname(os.path.abspath(__file__))
    config = os.path.join(dir, 'config', default_name)
    env_path = os.getenv(env_key, None)
    path = env_path if env_path else config
    if os.path.exists(path):
        with open(path, 'rt') as file:
            content = json.loads(file.read())
        logging.config.dictConfig(content)
    else:
        logging.basicConfig(level=default_level)
    global LOGGER
    LOGGER = logging.getLogger(__name__)
    http_handler = logging.handlers.HTTPHandler(
    RP_API.HOST,
    RP_API.LOG.format(project_name='default_project'),
    secure=True,
    method='POST',
    credentials=ErpActions.auth)
    LOGGER.addHandler(http_handler)
    http_handler.addFilter(RestFilter())


def pytest_addoption(parser):
    """
    Adds 2 optional parameters to the list of pytest:
    pytest [-E | --erp ]
    pytest [--project_name string]
    To activate report_portal transport use -E or --erp keys.
    If --projec_name option is not provided plugin will use name by default 'default_project'
    """
    group = parser.getgroup(name='report_portal', description="options for tuning epam's report portal")
    group.addoption('-E', '--erp', action='store_true', default=False, dest='is_erp',
                    help="Activate ability to send test info to epam's report portal")
    group.addoption('--project_name', action='store', dest='erp_proj', type='string', default='default_project',
                    help="Provide project name for sending test info to")
    group.addoption('--id', action='store', dest='launch_id', type='string', default='default_launch',
                    help="Name for the whole launch to be executed")
    group.addoption('--suite', action='store', dest='suite_name', type='string', default='default_suite',
                    help="Name for the suite under launch")
    setup_logging()


def pytest_configure(config):
    """
    Create instance of ReportPortal plugin if option -E or --erp is activated.
    """
    if config.option.is_erp:
        config._report_portal = ReportPortal()
        config.pluginmanager.register(config._report_portal)
        config.pluginmanager.unregister(name='python')


def pytest_unconfigure(config):
    """
    Unconfigure after working cycle.
    """
    report_portal = getattr(config, '_report_portal', None)
    if report_portal:
        del config._report_portal
        config.pluginmanager.unregister(report_portal)


class ReportPortal:
    """ Gathers information regarding each test in run time and send info to the REST service """

    active_test = None
    def __init__(self):
        self.project = None
        self.launch = None
        self.launch_id = None

    @pytest.mark.trylast
    def pytest_sessionstart(self, session):
        """
        Event to start launch on report portal.
        Shadows base pytest_sessionstart realization.
        """
        session._setupstate = ExtSetupState()
        session._fixturemanager = ExtFixtureManager(session)
        session.config.pluginmanager.import_plugin('python')
        self.project = session.config.option.erp_proj
        ItemState.project_name = self.project
        self.launch = session.config.option.launch_id
        self.suite_name = session.config.option.suite_name
        self.launch_id = ItemState(self.launch, self.suite_name, 'LAUNCH').activate().id
        LOGGER.info('Session is started. Launch num {}, project name {}, suite name {}'.format(self.launch_id,
                    self.project, self.suite_name))


    @pytest.mark.trylast
    def pytest_sessionfinish(self, session):
        """
        Event to finish entire launch on report portal.
        """
        ErpActions.finish(ItemState.current_session, 'PASSED')
        ErpActions.finish(id=self.launch_id, type='LAUNCH')
        LOGGER.info('Session is finished.')

    @pytest.mark.tryfirst
    def pytest_pycollect_makemodule(self, path, parent):
        """
        Do extending of base Module class in order to catch setup/teardown module fixtures.
        """
        return ExtModule(path, parent)

    @pytest.mark.trylast
    def pytest_pycollect_makeitem(self, __multicall__, collector, name, obj):
        """
        Either function or method should be wrapped to get ability react on setup/teardown event.
        """
        res = __multicall__.execute()
        if res is not None:
            return res
        if inspect.isclass(obj):
            if collector.classnamefilter(name):
                return ExtClass(name, parent=collector)
        elif collector.funcnamefilter(name) and hasattr(obj, '__call__') and \
                        getfixturemarker(obj) is None:
            if is_generator(obj):
                return Generator(name, parent=collector)
            else:
                func_for_wrap = list(collector._genfunctions(name, obj))
                func_for_wrap[:] = [ExtFunction(func) for func in func_for_wrap]
                return func_for_wrap

    def _activate_module(self, item):
        """
        Check if test belongs either current module or new one.
        If new module then create new suite instance and send to report portal.
        Store module object to ItemState.active_item_id.
        :param item: Test going to be executed.
        """
        get_module_name = lambda: ' '.join(str(item.module).split(os.path.sep)[-2:])[:-2]
        module = getattr(ItemState, 'current_module')
        if module and item.module is not ItemState.current_module.link:
            ItemState.current_class, ItemState.current_module = None, None

        if ItemState.current_module is None or item.module is not ItemState.current_module.link:
            name = get_module_name()
            ItemState.current_module = ItemState(name, item.module.__doc__, 'SUITE').activate()
            ItemState.current_module.link = item.module
            ItemState.active_item_id = ItemState.current_module.id
        return self

    def _activate_class(self, item):
        """
        Check if test belongs either current class or new one or just unbound function in class.
        If new class then create new Test item and send to report portal.
        Store class object to ItemState.active_item_id.
        :param item: Test going to be executed.
        """
        get_class_name = lambda: ' '.join((str(item.cls).split('.')[-1:]))[:-2]
        if item.cls:
            if ItemState.current_class is None or item.cls is not ItemState.current_class.link:
                ItemState.current_class = ItemState(get_class_name(), item.cls.__doc__, 'TEST').activate()
                ItemState.active_item_id = ItemState.current_class.id
                ItemState.current_class.link = item.cls
        else:
            ItemState.current_class = None
        return self

    def _activate_unbound_function(self, item):
        if not getattr(item, 'instance', None):
            item_wrap = ItemState(item.name + ' envelop', item.function.__doc__, 'TEST').activate()
            ItemState.current_unbound_method = item
            ItemState.active_item_id = item_wrap.id

    @pytest.mark.tryfirst
    def pytest_runtest_setup(self, item):
        """
        Function runs before every test item and checks if test belongs to module or module-class.
        :param item: Test going to be executed.
        """
        self._activate_module(item)._activate_class(item)._activate_unbound_function(item)

    @pytest.mark.tryfirst
    def pytest_runtest_call(self, item):
        """
        Send STEP item to report portal for each test, get function name and docstring.
        :param item: Test going to be executed.
        """
        self.active_test = ItemState(item.name, item.function.__doc__, 'STEP').activate()


    @pytest.mark.tryfirst
    def pytest_runtest_makereport(self, item, call,__multicall__):
        """
        Report sign for each event either passed or failed. If fail will immediately get control.
        """

        def _deactivate_fixture_afterfail():
            """
            When fixture fails it stops execution and drop out test this fixture belongs to.
            So we need send fail fo fixture and for current test which is not gonna be executed.

            """
            failure = item._repr_failure_py(excinfo, style=item.config.option.tbstyle)
            def simulate_test_after_fixturefail():
                """
                Send info regarding skipped test to report portal.
                """
                self.active_test = ItemState(item.name, item.function.__doc__, 'STEP').activate()
                self.active_test.stderr = failure
                self.active_test.failed = True

            ItemState.current_fixture.stderr = failure
            ItemState.current_fixture.failed = True
            ErpActions.log(ItemState.current_fixture)
            ItemState.current_fixture.here_and_now_deactivate()
            simulate_test_after_fixturefail()

        def fill_failed_test_info():
            self.active_test.stderr = item.repr_failure(excinfo)
            self.active_test.failed = True

        def deactivate_class():
            """
            If next test is in new class - deactivate current class and switch active focus to module.
            """
            if ItemState.item.cls != getattr(ItemState.nextitem, 'cls', None):
                ItemState.deactivate(ItemState.current_class.name)
                ItemState.active_item_id = ItemState.current_module.id

        def deactivate_module():
            """
            If next test is in new module - deactivate current one.
            """
            if ItemState.item.module != getattr(ItemState.nextitem, 'module', None):
                ItemState.deactivate(ItemState.current_module.name)

        def deactivate_unbound_method():
            """
            Next test is able to be in new module, new class, or just unbound method in the same class.
            For unbound method create envelop with the same name to fill in fixtures depends on this test.
            """
            def check_next():
                """
                If after unbound method new module or nothing - deactivate current module and return to prevent
                further verification and double sending.
                """
                if not ItemState.nextitem:
                    ItemState.deactivate(ItemState.current_module.name)
                deactivate_module()
                return False

            if ItemState.current_unbound_method:
                ItemState.deactivate(ItemState.current_unbound_method.name + ' envelop')
                ItemState.current_unbound_method = None
                ItemState.active_item_id = ItemState.current_module.id
                return check_next()
            return True

        when, excinfo = call.when, call.excinfo

        # check whether failure on before or test stage.
        if excinfo:
            if when == 'setup':
                _deactivate_fixture_afterfail()
            if when == 'call':
                fill_failed_test_info()

        # if failure doesnt appear code will follow this way, do teardown for each success test.
        if when == 'teardown':
            if not deactivate_unbound_method():
                return
            deactivate_class()
            deactivate_module()


    @pytest.mark.tryfirst
    def pytest_runtest_teardown(self, item, nextitem):
        ItemState.item, ItemState.nextitem = item, nextitem
        self.active_test.stdout = self.active_test.item.outerr
        ErpActions.log(self.active_test)
        ItemState.here_and_now_deactivate(self.active_test)







