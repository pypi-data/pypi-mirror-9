from collections import namedtuple
import logging
from pytest_plugin.custom_exceptions import MoreThanOneFound, NothingFound
from pytest_plugin.rest_erp_client import ErpActions

__author__ = 'kiryl_zayets'

mapping = namedtuple('mapping', ['action', 'scope', 'cached_res', 'autouse'])


def fixture_info(scope=None, action=ErpActions.start, cached_res=None, autouse=None):
    return mapping(action, scope, cached_res, autouse)


class ItemState(object):
    project_name = None
    items = []
    active_item_id = None
    current_session = None
    current_module = None
    current_class = None
    current_fixture = None
    current_unbound_method = None
    item = None
    nextitem = None


    def __init__(self, name, desc=None, type=None, fixture_mapping=None, action=ErpActions.start, failed=False, out=None, err=None):
        self.id = None
        self.name, self.desc, self.type = name, desc, type
        self.fixture = fixture_mapping
        self.failed = False
        self.exc_info = ''
        self.stdout, self.stderr = out, err
        self(action)

    def __call__(self, *args, **kwargs):
        if self.fixture:
            self.action = self.fixture.action
        else:
            self.action = args[0]


    def activate(self):
        self.action(self)
        self.items.append(self)
        return self

    def here_and_now_deactivate(self):
        event = [i for i in reversed(self.items) if i is self][0]
        self.items.remove(event)
        if event.stderr:
            ErpActions.finish(event.id, 'FAILED')
        else:
            ErpActions.finish(event.id, 'PASSED')

    @classmethod
    def deactivate(cls, item):
        LOGGER = logging.getLogger(__name__)
        if item:
            repr = str(item)
            current_event = [i for i in reversed(cls.items) if repr.find(i.name) != -1]
            try:
                if len(current_event) > 1:
                    raise MoreThanOneFound('Several finalizers found {}'.format(current_event))
                if len(current_event) == 0:
                    raise NothingFound('No one finalizer is found in the list {0}. Was trying to found {1}'.format(cls, repr))

                if not current_event[0].failed:
                    ErpActions.finish(current_event[0].id, 'PASSED')
                else:
                    ErpActions.finish(current_event[0].id, 'FAILED')
                try:
                    cls.items.remove(current_event[0])
                except (AttributeError, IndexError):
                    LOGGER.error('Item to be deleted is not present in collection of events', exc_info=True)
            except (NothingFound, MoreThanOneFound):
                LOGGER.error('Problems with finalizer occured, please check list {} and item {}'.
                             format(cls, repr), exc_info=True)


    def __str__(self):
        names  = [(i.name, i.id) for i in self.items]
        return ''.join(names)