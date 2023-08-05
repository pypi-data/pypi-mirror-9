import inspect
import sys
from io import StringIO
from types import MethodType

import _pytest
from _pytest.python import fillfixtures, xunitsetup, Instance, FixtureManager, NOTSET, getfixturemarker, \
    defaultfuncargprefixmarker, FixtureFunctionMarker, call_fixture_func, getimfunc
import py
import pytest
from pytest_plugin.mapping_fixture_action import ItemState, fixture_info
from pytest_plugin.rest_erp_client import ErpActions


__author__ = 'kiryl_zayets'


class ExtModule(_pytest.python.Module):
    def setup(self):
        setup_module = xunitsetup(self.obj, "setUpModule")
        if setup_module is None:
            setup_module = xunitsetup(self.obj, "setup_module")
        try:
            if setup_module is not None:
                if inspect.getargspec(setup_module)[0]:
                    setup_module(self.obj)
                else:
                    setup_module()
        except Exception:
            info = sys.exc_info()
            raise
        # else:
        #     item = ItemState(fixture_info(FixtureMapping.BEFORE_TEST))
        #     item.name = "setup_module"
        #     item.activate()

        fin = getattr(self.obj, 'tearDownModule', None)
        if fin is None:
            fin = getattr(self.obj, 'teardown_module', None)
        if fin is not None:
            if inspect.getargspec(fin)[0]:
                finalizer = lambda: fin(self.obj)
            else:
                finalizer = fin
            # item.has_teardown = True

            self.addfinalizer(finalizer)


class ExtClass(_pytest.python.Class):
    def setup(self):
        setup_class = xunitsetup(self.obj, 'setup_class')
        if setup_class is not None:
            setup_class = getattr(setup_class, 'im_func', setup_class)
            setup_class = getattr(setup_class, '__func__', setup_class)
            setup_class(self.obj)
            # item = ItemState(fixture_info(FixtureMapping.
            #                               BEFORE_CLASS))
            # item.name = 'setup_class'
            # item.activate(item)
        fin_class = getattr(self.obj, 'teardown_class', None)
        if fin_class is not None:
            fin_class = getattr(fin_class, 'im_func', fin_class)
            fin_class = getattr(fin_class, '__func__', fin_class)
            self.addfinalizer(lambda: fin_class(self.obj))
            # item.has_teardown = True


class ExtFunctionMixin(_pytest.python.FunctionMixin):
    def setup(self):
        """ perform setup for this test function. """
        if hasattr(self, '_preservedparent'):
            obj = self._preservedparent
        elif isinstance(self.parent, Instance):
            obj = self.parent.newinstance()
            self.obj = self._getobj()
        else:
            obj = self.parent.obj
        if inspect.ismethod(self.obj):
            setup_name = 'setup_method'
            teardown_name = 'teardown_method'
            # item = ItemState(fixture_info(FixtureMapping.BEFORE_METHOD))
            # item.name = 'setup_method'
        else:
            setup_name = 'setup_function'
            teardown_name = 'teardown_function'
            # item = ItemState(fixture_info(FixtureMapping.BEFORE_FUNCTION))
            # item.name = 'setup_function'
        setup_func_or_method = xunitsetup(obj, setup_name)
        if setup_func_or_method is not None:
            setup_func_or_method(self.obj)
            # item.activate(item)
        fin = getattr(obj, teardown_name, None)
        if fin is not None:
            self.addfinalizer(lambda: fin(self.obj))
            # item.has_teardown = True


class ExtFunction(_pytest.python.Function):
    def __init__(self, wrappee):
        self.wrappee = wrappee

    def __getattr__(self, item):
        return getattr(self.wrappee, item)

    def __setattr__(self, key, value):
        if key is 'wrappee':
            self.__dict__[key] = value
        else:
            self.__dict__['wrappee'].__dict__[key] = value

    def setup(self):
        try:
            self.callspec._emptyparamspecified
        except AttributeError:
            pass
        else:
            fs, lineno = self._getfslineno()
            pytest.skip("got empty parameter set, function %s at %s:%d" % (
                self.function.__name__, fs, lineno))
        ExtFunctionMixin.setup(self)
        try:
            request = self._request
            self._request._pyfuncitem = self._pyfuncitem
        except:
            fillfixtures(self)
        else:
            item = request._pyfuncitem
            fixturenames = getattr(item, "fixturenames", request.fixturenames)
            for argname in fixturenames:
                if argname not in item.funcargs:
                    item.funcargs[argname] = request.getfuncargvalue(argname)


class ExtSetupState(_pytest.runner.SetupState):
    def _callfinalizers(self, colitem):
        finalizers = self._finalizers.pop(colitem, None)
        exc = None
        while finalizers:
            fin = finalizers.pop()
            try:
                fin()
                # if str(fin).find('ExtFunctionMixin.setup') > 0:
                #     if inspect.ismethod(colitem.obj):
                #         ItemState.deactivate('setup_method')
                #     else:
                #         ItemState.deactivate('setup_function')
                # elif str(fin).find('ExtModule.setup') > 0:
                #     ItemState.deactivate('setup_module')
                # elif str(fin).find('ExtClass.setup') > 0:
                #     ItemState.deactivate('setup_class')
            except Exception:
                if exc is None:
                    exc = sys.exc_info()
        if exc:
            py.builtin._reraise(*exc)


class ExtFixtureManager(FixtureManager):
    def parsefactories(self, node_or_obj, nodeid=NOTSET, unittest=False):
        if nodeid is not NOTSET:
            holderobj = node_or_obj
        else:
            holderobj = node_or_obj.obj
            nodeid = node_or_obj.nodeid
        if holderobj in self._holderobjseen:
            return
        self._holderobjseen.add(holderobj)
        autousenames = []
        for name in dir(holderobj):
            obj = getattr(holderobj, name, None)
            if not callable(obj):
                continue
            # fixture functions have a pytest_funcarg__ prefix (pre-2.3 style)
            # or are "@pytest.fixture" marked
            marker = getfixturemarker(obj)
            if marker is None:
                if not name.startswith(self._argprefix):
                    continue
                marker = defaultfuncargprefixmarker
                name = name[len(self._argprefix):]
            elif not isinstance(marker, FixtureFunctionMarker):
                # magic globals  with __getattr__ might have got us a wrong
                # fixture attribute
                continue
            else:
                assert not name.startswith(self._argprefix)
            fixturedef = ExtFixtureDef(self, nodeid, name, obj,
                                       marker.scope, marker.params,
                                       yieldctx=marker.yieldctx,
                                       unittest=unittest, ids=marker.ids)
            faclist = self._arg2fixturedefs.setdefault(name, [])
            if fixturedef.has_location:
                faclist.append(fixturedef)
            else:
                # fixturedefs with no location are at the front
                # so this inserts the current fixturedef after the
                # existing fixturedefs from external plugins but
                # before the fixturedefs provided in conftests.
                i = len([f for f in faclist if not f.has_location])
                faclist.insert(i, fixturedef)
            if marker.autouse:
                autousenames.append(name)
        if autousenames:
            self._nodeid_and_autousenames.append((nodeid or '', autousenames))


class ExtFixtureDef(_pytest.python.FixtureDef):

    def execute(self, request):
        # get required arguments and register our own finish()
        # with their finalization
        kwargs = {}
        for argname in self.argnames:
            fixturedef = request._get_active_fixturedef(argname)
            result, arg_cache_key = fixturedef.cached_result
            kwargs[argname] = result
            if argname != "request":
                fixturedef.addfinalizer(self.finish)

        my_cache_key = request.param_index
        cached_result = getattr(self, "cached_result", None)
        if cached_result is not None:
            # print argname, "Found cached_result", cached_result
            # print argname, "param_index", param_index
            result, cache_key = cached_result
            if my_cache_key == cache_key:
                # print request.fixturename, "CACHE HIT", repr(my_cache_key)
                return result
            # print request.fixturename, "CACHE MISS"
            # we have a previous but differently parametrized fixture instance
            # so we need to tear it down before creating a new one
            self.finish()
            assert not hasattr(self, "cached_result")

        if self.unittest:
            result = self.func(request.instance, **kwargs)
        else:
            fixturefunc = self.func
            # the fixture function needs to be bound to the actual
            # request.instance so that code working with "self" behaves
            # as expected.
            if request.instance is not None:
                fixturefunc = getimfunc(self.func)
                if fixturefunc != self.func:
                    fixturefunc = fixturefunc.__get__(request.instance)

            old_std, old_err = sys.stdout, sys.stderr
            new_one_info, new_one_error = StringIO(), StringIO()
            sys.stdout, sys.stderr = new_one_info, new_one_error

            _fixture = fixture_info(self.scope, ErpActions.fixture, None, fixturefunc._pytestfixturefunction.autouse)
            item = ItemState(self.argname, fixturefunc.__doc__, fixture_mapping=_fixture).activate()
            ItemState.current_fixture = item
            result = call_fixture_func(fixturefunc, request, kwargs,
                                       self.yieldctx)
            # _fixture(result)

            info = new_one_info.getvalue()
            err = new_one_error.getvalue()
            sys.stdout, sys.stderr = old_std, old_err
            item.stdout, item.stderr = info, err
            # item = ItemState(self.argname, fixturefunc.__doc__, fixture_mapping=_fixture, out=info, err=err).activate()
            ErpActions.log(item)
            item.here_and_now_deactivate()
        self.cached_result = (result, my_cache_key)
        return result


    def finish(self):
        """
        Finale for fixtures
        """
        while self._finalizer:
            func = self._finalizer.pop()
            old_std, old_err = sys.stdout, sys.stderr
            new_one_info, new_one_error = StringIO(), StringIO()
            sys.stdout, sys.stderr = new_one_info, new_one_error
            func()
            info = new_one_info.getvalue()
            err = new_one_error.getvalue()
            sys.stdout, sys.stderr = old_std, old_err
            if not type(func) is MethodType:
                _fixture = fixture_info(scope=self.scope, action=ErpActions.start_teardown_fixture)
                item = ItemState(self.argname,func.__doc__,  fixture_mapping=_fixture, out=info, err=err).activate()
                ErpActions.log(item)
                item.here_and_now_deactivate()
        try:
            del self.cached_result
        except AttributeError:
            pass