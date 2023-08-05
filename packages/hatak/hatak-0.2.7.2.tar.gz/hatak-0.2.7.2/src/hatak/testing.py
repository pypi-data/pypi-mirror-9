from mock import MagicMock, patch
from pytest import fixture, yield_fixture

import hatak
from hatak.unpackrequest import unpack


class ApplicatonFixture(object):

    @fixture(scope="session")
    def app(self):
        return hatak._test_cache['app']


class RequestFixture(ApplicatonFixture):

    def _get_default_request(self, app):
        request = MagicMock()
        request.registry = {
            'unpacker': app.unpacker,
            'settings': {},
            'paths': {},
        }
        return request

    @fixture
    def request(self, app):
        request = self._get_default_request(app)
        unpack(self, request)
        return request


class ControllerFixture(RequestFixture):

    def _get_controller_class(self):
        pass

    @fixture
    def root_tree(self):
        return MagicMock()

    @fixture
    def data(self):
        return {}

    @fixture
    def matchdict(self):
        return {}

    @fixture
    def controller(self, app, request, root_tree, data, matchdict):
        request.registry['controller_plugins'] = app.controller_plugins
        controller = self._get_controller_class()(root_tree, request)
        controller.data = data
        controller.matchdict = matchdict
        return controller


class FormFixture(object):

    @yield_fixture
    def CsrfMustMatch(self):
        with patch('haplugin.formskit.models.CsrfMustMatch') as mock:
            yield mock

    def _create_fake_post(self, data):
        defaults = {
            self.form.form_name_value: [self.form.get_name(), ]
        }
        defaults.update(data)
        self.POST.dict_of_lists.return_value = defaults


class PluginFixture(ApplicatonFixture):

    def _get_plugin_class(self):
        pass

    @fixture
    def fake_app(self):
        return MagicMock()

    @fixture
    def fake_config(self, fake_app):
        return fake_app.config

    @fixture
    def plugin(self, fake_app):
        plugin = self._get_plugin_class()
        plugin.app = fake_app
        return plugin
