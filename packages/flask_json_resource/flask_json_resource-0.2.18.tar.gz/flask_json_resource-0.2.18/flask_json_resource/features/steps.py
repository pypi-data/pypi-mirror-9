import re
import json
from urlparse import urljoin

import requests
from json_pointer import Pointer

from pytest_bdd import given, when, then


@given('access to the API')
def context():
    class Context(object):
        pass

    context = Context()
    context.session = requests.session()
    return context


@when(re.compile('I have a (?P<resource>\w+) resource: (?P<data>.+)'))
def insert_resource(app, context, resource, data):
    data = json.loads(data)

    with app.test_request_context():
        resource = getattr(context.resources, resource)(data)

        resource.save()


@given(re.compile('a (?P<resource>\w+) resource: (?P<data>.+)'))
def given_resource(app, context, resource, data):
    insert_resource(app, context, resource, data)


@given(re.compile('also a (?P<resource>\w+) resource: (?P<data>.+)'))
def also_give(app, context, resource, data):
    insert_resource(app, context, resource, data)


@when(re.compile('I create a (?P<resource>\w+) resource: (?P<data>.+)'))
def create_resource(app, context, resource, data):
    data = json.loads(data)

    with app.test_request_context():
        resource = getattr(context.resources, resource)(data)
        resource.save(create=True)

        context.resource = resource



@given(re.compile('I use "(?P<value>.+)" as the "(?P<header>.+)" header'))
def given_header(context, header, value):
    context.session.headers.update({header: value})


@when(re.compile('I set the "(?P<header>.+)" header to "(?P<value>.+)"'))
def set_header(context, header, value):
    """ Set the http header `header` to `value`"""
    given_header(context, header, value)


@when(re.compile('I make a (?P<method>.+) request to "(?P<path>(\S+))" with outlined data: (?P<data>.+)'))
def api_request_with_data_outline(api_server, context, method, path, request_data):
    """ Make a request to `path` using `method`. If this step contains
    text, use that as the body
    """
    api_request_with_data(api_server, context, method, path, request_data)


@when(re.compile('I make a (?P<method>.+) request to "(?P<path>(\S+))" with data: (?P<data>.+)'))
def api_request_with_data(api_server, context, method, path, data):
    """ Make a request to `path` using `method`. If this step contains
    text, use that as the body
    """
    func = getattr(context.session, method.lower())

    context.response = func(urljoin(api_server.url, path), data=data)


@when(re.compile('I make a (?P<method>.+) request to "(?P<path>(\S+))"$'))
def api_request(api_server, context, method, path):
    """ Make a request to `path` using `method`.
    """
    api_request_with_data(api_server, context, method, path, None)


@then(re.compile('the response status should be (?P<status>\d+)'))
def status_code(context, status):
    """ Make sure the response status code is `status`"""
    assert context.response.status_code == int(status)


@then(re.compile('the response status should be <status>'))
def status_outlined(context, status):
    status_code(context, status)


@then(re.compile('the response data should be: (?P<data>.+)'))
def data(context, data):
    """ Make sure the response body is equal to the text"""
    expected = json.loads(data)
    found = json.loads(context.response.content)
    assert expected == found


@then(re.compile('"(?P<pointer>.+)" should contain "(?P<value>.+)"'))
def contains(context, pointer, value):
    pointer = Pointer(pointer)

    data = json.loads(context.response.content)
    assert value == json.dumps(pointer.get(data))


@then(re.compile('the size of "(?P<pointer>.+)" should be (?P<value>.+)'))
def pointer_size(context, pointer, value):
    pointer = Pointer(pointer)

    data = json.loads(context.response.content)

    assert int(value) == len(pointer.get(data))


@then(re.compile('the "(?P<header>.+)" header should be "(?P<value>.+)"'))
def header(context, header, value):
    """ Make sure the response header `header` is equal to `value`"""
    assert context.response.headers[header] == value


@then(re.compile('the "(?P<relation>.+)" relation should be "(?P<url>.+)"'))
def relation(context, relation, url):
    """Make sure the link relation in the response is equal to `url`"""
    assert context.response.links[relation]['url'] == url
