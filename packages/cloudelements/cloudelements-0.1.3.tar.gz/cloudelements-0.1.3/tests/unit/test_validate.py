import pytest
from mock import patch


def test_validate_decorator():
    from cloudelements.validation import validate_schema

    schema = {
        'type': 'object',
        'properties': {
            'first': {
                'type': 'string',
                'minLength': 1,
                'blank': False
            },
            'last': {
                'type': 'integer'
            }
        }
    }

    class TempClass(object):

        @validate_schema(schema=schema)
        def temp_func_single(self, data):
            return True

        @validate_schema(schema=schema)
        def temp_func_double(self, id, data):
            return True

    @validate_schema(schema=schema)
    def temp_func_alone(data):
        return True

    tmp_cls = TempClass()
    resp = tmp_cls.temp_func_single(dict(first='foo', last=1))
    assert resp is True
    resp = tmp_cls.temp_func_double(1, dict(first='foo', last=1))
    assert resp is True
    resp = temp_func_alone(dict(first='foo', last=1))
    assert resp is True


def test_validate_decorator_fails():
    from cloudelements.validation import validate_schema
    from cloudelements.validation import NoDataException, ValidationError

    schema = {
        'type': 'object',
        'properties': {
            'first': {
                'type': 'string',
                'minLength': 1,
                'blank': False
            },
            'last': {
                'type': 'integer'
            }
        }
    }

    @validate_schema(schema=schema)
    def temp_func(data):
        return True

    resp = temp_func(dict(first='foo', last='foo'))
    assert resp == [{'error': 'foo', 'field': 'last', 'msg': "Value 'foo' for field '<obj>.last' is not of type integer"}]
