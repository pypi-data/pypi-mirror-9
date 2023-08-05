from .liveserver import LiveServer
from .main import app, Message


def before_all(context):
    context.app = app
    context.live_server = LiveServer(context.app)
    context.live_server.start()

    context.url = context.live_server.url


def after_all(context):
    context.live_server.stop()


def before_scenario(context, scenario):
    context.headers = {}
    context.htt_mocks = []


def after_scenario(context, scenario):
    with context.app.app_context():
        Message.objects.collection.remove()
