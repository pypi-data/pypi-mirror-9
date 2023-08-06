import pytest

from flask_json_resource.features.liveserver import LiveServer
from flask_json_resource.features.main import app, Message
from flask_json_resource.features.steps import *


@pytest.fixture(scope='module')
def api_server(request):
    print 'Setup LiveServer'
    api_server = LiveServer(app)
    api_server.start()

    def fin():
        print 'Teardown LiveServer'
        api_server.stop()

    request.addfinalizer(fin)
    return api_server


def pytest_runtest_teardown(item, nextitem):
    with app.app_context():
        Message.objects.collection.remove()

