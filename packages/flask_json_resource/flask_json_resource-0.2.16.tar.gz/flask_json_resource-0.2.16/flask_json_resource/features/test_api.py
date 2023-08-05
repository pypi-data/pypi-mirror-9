import json
import re

from pytest_bdd import scenario, given, when

from .main import app, Message


@scenario('resource.feature', 'Retrieve non-existing message')
def test_retrieve_non_existing():
    pass


@scenario('resource.feature', 'Retrieve existing message')
def test_retrieve():
    pass


@scenario('resource.feature', 'Delete a message')
def test_delete():
    pass


@scenario('resource.feature', 'Get after delete message')
def test_get_after_delete():
    pass


@scenario('resource.feature', 'Delete a non-existing message')
def test_delete_non_existing():
    pass


@scenario('resource.feature', 'PUT a message')
def test_put():
    pass


@scenario('resource.feature', 'PUT a non-existing message')
def test_put_non_existing():
    pass


@scenario('resource.feature', 'PUT an invalid message')
def test_put_invalid_message():
    pass


@scenario('resource.feature', 'PUT an invalid json')
def test_put_invalid_json():
    pass


@scenario('resource.feature', 'POST a message')
def test_post():
    pass


@scenario('resource.feature', 'POST a message that already exists')
def test_post_existing():
    pass


@scenario('resource.feature', 'POST an invalid message')
def test_post_invalid_message():
    pass


@scenario('resource.feature', 'POST an invalid json message')
def test_post_invalid_json():
    pass


@scenario('collection.feature', 'Retrieve all message')
def test_retrieve_all():
    pass


@given(re.compile(r'an existing message: (?P<text>.+)'))
def message(text):
    """
    Store a single test message in the database
    """
    with app.app_context():
        message = Message(
            json.loads(text)
        )

        message.save()


@when(re.compile(r'I insert a message: (?P<text>.+)'))
def message_insert(text):
    message(text)



