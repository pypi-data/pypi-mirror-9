import pytest

from mock import patch, MagicMock, PropertyMock
from contextlib import nested

import httpretty


class MockResponse(object):
    status_code = 200

    def json(self):
        return dict(status_code=200, result=dict(foo='bar'))


@patch('cloudelements.requests.get')
def test_base_class_can_use_methods(mock_get):
    from cloudelements import BaseRequest
    with patch('cloudelements.requests.Response') as mock_response:
        mock_response = MockResponse()
        mock_get.return_value = mock_response
        req = BaseRequest(base_url='http://www.foo.com/')
        response = req._get('/', params=dict(foo='bar'))
        assert response.status_code == 200
        assert response.json() == dict(status_code=200, result=dict(foo='bar'))


@patch('cloudelements.requests.post')
def test_base_class_can_use_post(mock_get):
    from cloudelements import BaseRequest
    with patch('cloudelements.requests.Response') as mock_response:
        mock_response = MockResponse()
        mock_get.return_value = mock_response
        req = BaseRequest()
        req.base_url = 'http://www.foo.com/'
        response = req._post('/', data=[])
        assert response.status_code == 200
        assert response.json() == dict(status_code=200, result=dict(foo='bar'))


@patch('cloudelements.requests.delete')
def test_base_class_can_use_delete(mock_get):
    from cloudelements import BaseRequest
    with patch('cloudelements.requests.Response') as mock_response:
        mock_response = MockResponse()
        mock_get.return_value = mock_response
        req = BaseRequest()
        req.base_url = 'http://www.foo.com/'
        response = req._delete('/')
        assert response.status_code == 200
        assert response.json() == dict(status_code=200, result=dict(foo='bar'))


@patch('cloudelements.requests.put')
def test_base_class_can_use_put(mock_get):
    from cloudelements import BaseRequest
    with patch('cloudelements.requests.Response') as mock_response:
        mock_response = MockResponse()
        mock_get.return_value = mock_response
        req = BaseRequest('http://www.foo.com/')
        response = req._put('/', data=[])
        assert response.status_code == 200
        assert response.json() == dict(status_code=200, result=dict(foo='bar'))


@httpretty.activate
def test_base_request_get():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.GET,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._get('v1/emailguess/job/status/1')
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_get_with_params():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.GET,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._get('v1/emailguess/job/status/1', params=dict(foo='bar'))
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_get_fourohfour():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.GET,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json",
        status=404
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._get('v1/emailguess/job/status/1')
    assert resp.status_code == 404
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_get_with_auth_token():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.GET,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json",
        status=200
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._get('v1/emailguess/job/status/1', auth_token='adsfasdf')
    assert resp.status_code == 200
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_post():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.POST,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._post('v1/emailguess/job/status/1', data=dict(foo='bar'))
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_put():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.PUT,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._put('v1/emailguess/job/status/1', data=dict(foo='bar'))
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_patch():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.PATCH,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._patch('v1/emailguess/job/status/1', data=dict(foo='bar'))
    assert resp.json() == dict(foo='bar', baz=2)


@httpretty.activate
def test_base_request_send_request_not_method():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.GET,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._send_request(
        'v1/emailguess/job/status/1',
        method='FOO',
        data=dict(foo='bar')
    )
    assert resp is None


@httpretty.activate
def test_base_request_delete():
    from cloudelements import BaseRequest
    httpretty.register_uri(
        httpretty.DELETE,
        'http://api.leadgenius.com/v1/emailguess/job/status/1',
        body='{ "foo": "bar", "baz": 2}',
        content_type="application/json"
    )

    req = BaseRequest('http://api.leadgenius.com/')
    resp = req._delete('v1/emailguess/job/status/1')
    assert resp.json() == dict(foo='bar', baz=2)
