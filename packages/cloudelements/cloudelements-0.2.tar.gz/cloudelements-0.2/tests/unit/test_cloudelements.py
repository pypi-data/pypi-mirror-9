import pytest
import unittest

from mock import patch, MagicMock, PropertyMock
from contextlib import nested

import httpretty
import re


class TestCloudElements(unittest.TestCase):
    def setUp(self):
        from cloudelements import CloudElements
        self.cloud_elements = CloudElements(
            user_secret='',
            org_secret=''
        )


class TestHub(TestCloudElements):
    def setUp(self):
        super(TestHub, self).setUp()
        self.hub_path = \
            re.compile('%s/hubs.*' % self.cloud_elements.base_url)

    @httpretty.activate
    def test_get_hubs(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            self.hub_path,
            body=json.dumps([{'foo': 1}])
        )

        resp = ce.get_hubs()
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        assert hubs.pop() == {'foo': 1}

    @httpretty.activate
    def test_hubs_keys(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            self.hub_path,
            body=json.dumps([{'foo': 1}])
        )

        resp = ce.get_hubs_keys()
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        assert hubs.pop() == {'foo': 1}

    @httpretty.activate
    def test_get_hub_key(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            self.hub_path,
            body=json.dumps([{'foo': 1}])
        )

        resp = ce.get_hub_key(key='bar')
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        assert hubs.pop() == {'foo': 1}

    @httpretty.activate
    def test_get_hub_key_for_elements(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            self.hub_path,
            body=json.dumps([{'foo': 1}])
        )

        resp = ce.get_hub_key_for_elements(key='bar')
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        assert hubs.pop() == {'foo': 1}


class TestCRMHub(TestCloudElements):
    @httpretty.activate
    def test_get_accounts(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.cloud_elements.base_url +
                self.cloud_elements.paths['accounts_crm'],
            body=json.dumps({'foo': 1})
        )

        resp = self.cloud_elements.get_crm_accounts('where id=1')
        assert resp.json() == {'foo': 1}

    @httpretty.activate
    def test_create_accounts(self):
        import json
        httpretty.register_uri(
            httpretty.POST,
            self.cloud_elements.base_url +
                self.cloud_elements.paths['accounts_crm'],
            body=json.dumps({'foo': 1})
        )

        resp = self.cloud_elements.create_crm_accounts({'name': 'Gangta G Funk'})
        assert resp.json() == {'foo': 1}

    @httpretty.activate
    def test_get_account_by_id(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.cloud_elements.base_url +
                '%s/%s' % (self.cloud_elements.paths['accounts_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_account_by_id(acct_id=1)
        assert resp.json() == {'foo': 1}

    @httpretty.activate
    def test_update_account_by_id(self):
        import json
        httpretty.register_uri(
            httpretty.PATCH,
            self.cloud_elements.base_url +
                 '%s/%s' % (self.cloud_elements.paths['accounts_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements. \
            update_crm_account_by_id(acct_id=1, data={'name': 'Mario'})
        assert resp.json() == {'foo': 1}

    @httpretty.activate
    def test_delete_account_by_id(self):
        import json
        httpretty.register_uri(
            httpretty.DELETE,
            self.cloud_elements.base_url +
                '%s/%s' % (self.cloud_elements.paths['accounts_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.delete_crm_account_by_id(acct_id=1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.DELETE

    @httpretty.activate
    def test_create_bulk_query(self):
        import json
        httpretty.register_uri(
            httpretty.POST,
            self.cloud_elements.base_url
                + self.cloud_elements.paths['bulk_crm']
                + "/query?q=where 1 is 1",
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.create_crm_bulk_job(query='where 1 is 1')
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.POST

    @httpretty.activate
    def test_bulk_query(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.cloud_elements.base_url
                + self.cloud_elements.paths['bulk_crm']
                + "/query?q=where 1 is 1",
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.bulk_crm_query(query='where 1 is 1')
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_get_bulk_job_status(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.cloud_elements.base_url
                + self.cloud_elements.paths['bulk_crm']
                + '/1/status',
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_bulk_job_status(job_id=1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_get_bulk_job_errors(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.cloud_elements.base_url
                + self.cloud_elements.paths['bulk_crm']
                + '/1/errors',
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_bulk_job_errors(job_id=1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_get_bulk_job_object(self):
        import json

        url = '{base_url}{path}/{object_id}/{object_name}' \
            .format(
                base_url=self.cloud_elements.base_url,
                path=self.cloud_elements.paths['bulk_crm'],
                object_id=1,
                object_name='foo'
            )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps({'foo': 1})
        )
        resp = \
            self.cloud_elements \
            .get_crm_bulk_job_object(job_id=1, object_name='foo')
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_create_crm_bulk_objects(self):
        assert (
            self.cloud_elements.create_crm_bulk_objects('obj', 1, 12) is None
        )

    @httpretty.activate
    def test_get_contacts(self):
        import json
        ce = self.cloud_elements

        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + ce.paths['contacts_crm'],
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_contacts(query="where id=1")
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_create_contact(self):
        import json
        ce = self.cloud_elements

        httpretty.register_uri(
            httpretty.POST,
            ce.base_url + ce.paths['contacts_crm'],
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.create_crm_contact({'lastname': 'foo'})
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.POST

    @httpretty.activate
    def test_update_contact(self):
        import json
        ce = self.cloud_elements

        httpretty.register_uri(
            httpretty.PATCH,
            ce.base_url + ce.paths['contacts_crm'] + '/1',
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.update_crm_contact(1, {'lastname': 'foo'})
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.PATCH

    @httpretty.activate
    def test_delete_contact(self):
        import json
        ce = self.cloud_elements

        httpretty.register_uri(
            httpretty.DELETE,
            ce.base_url + '%s/%s' % (ce.paths['contacts_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.delete_crm_contact(1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.DELETE

    @httpretty.activate
    def test_get_contact(self):
        import json
        ce = self.cloud_elements

        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + '%s/%s' % (ce.paths['contacts_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_contact(1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_get_leads(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url  + ce.paths['leads_crm'],
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_leads(query='where id=1')
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_create_lead(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.POST,
            ce.base_url + ce.paths['leads_crm'],
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements\
            .create_crm_lead({'lastname': 'foo' , 'company': 'foo', 'status': 'somestatus'})
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.POST

    @httpretty.activate
    def test_get_lead(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + '%s/%s' % (ce.paths['leads_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.get_crm_lead(1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.GET

    @httpretty.activate
    def test_update_lead(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.PATCH,
            ce.base_url + '%s/%s' % (ce.paths['leads_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.\
            update_crm_lead(1, {'lastname': 'foo', 'company': 'foo', 'status': 'somestatus'})
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.PATCH

    @httpretty.activate
    def test_delete_lead(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.DELETE,
            ce.base_url + '%s/%s' % (ce.paths['leads_crm'], 1),
            body=json.dumps({'foo': 1})
        )
        resp = self.cloud_elements.delete_crm_lead(1)
        assert resp.json() == {'foo': 1}
        assert httpretty.last_request().method == httpretty.DELETE


class TestElements(TestCloudElements):
    def setUp(self):
        super(TestElements, self).setUp()
        self.url_re = \
            re.compile('%s/elements.*' % self.cloud_elements.base_url)

    @httpretty.activate
    def test_get_all_elements(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_all_elements()
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_all_element_keys(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_all_element_keys()
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_element_by_key(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_element_by_key(key='id')
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_element_config_by_key(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_element_config_by_key(key='id')
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_element_oauth_token(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_element_oauth_token(key='id')
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_sales_force_provision_url(self):
        import json
        httpretty.register_uri(
            httpretty.GET,
            self.url_re,
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.get_sales_force_provision_url(
            key='foo',
            secret='bar',
            callback_url='http://test.com'
        )
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')


class TestInstances(TestCloudElements):
    @httpretty.activate
    def test_crm_provision_instance(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.POST,
            ce.base_url + ce.paths['instances'],
            body=json.dumps(dict(foo='bar'))
        )
        resp = self.cloud_elements.provision_sales_force_instance(
            key='foo',
            secret='bar',
            callback_url='http://test.com',
            name='test',
            code='blahblah',
            tags=['foo']
        )
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_instances(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + ce.paths['instances'],
            body=json.dumps(dict(foo='bar'))
        )
        resp = ce.get_instances()
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_instance(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + ce.paths['instances'] + '/1',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.get_instance(1)
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_delete_instance(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.DELETE,
            ce.base_url + ce.paths['instances'] + '/1',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.delete_instance(1)
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_update_instance(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.PUT,
            ce.base_url + ce.paths['instances'] + '/1',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.update_instance(1, data={
            'element': {
                'key': 'sfdc',
                'id': 1
            },
            'providerData': {
                'code': 'foo'
            },
            'name': 'bar'
        })
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_create_instance(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.POST,
            ce.base_url + ce.paths['instances'],
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.create_instance(data={
            'element': {
                'key': 'sfdc',
                'id': 1
            },
            'providerData': {
                'code': 'foo'
            },
            'name': 'bar'
        })
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_instance_transformations(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + ce.paths['instances'] + '/1/transformations',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.get_instance_transformations(1)
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_delete_instance_transformations(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.DELETE,
            ce.base_url + ce.paths['instances'] + '/1/transformations',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.delete_instance_transformations(1)
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_create_instance_transformation(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.POST,
            ce.base_url + ce.paths['instances'] + '/1/transformations/obj',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.create_instance_transformation(1, object_name='obj', data={})
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_delete_instance_transformation(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.DELETE,
            ce.base_url + ce.paths['instances'] + '/1/transformations/obj',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.delete_instance_transformation(1, object_name='obj')
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_get_instance_transformation(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.GET,
            ce.base_url + ce.paths['instances'] + '/1/transformations/obj',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.get_instance_transformation(1, object_name='obj')
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')

    @httpretty.activate
    def test_update_instance_transformation(self):
        import json
        ce = self.cloud_elements
        httpretty.register_uri(
            httpretty.PUT,
            ce.base_url + ce.paths['instances'] + '/1/transformations/obj',
            body=json.dumps(dict(foo='bar'))
        )

        resp = ce.update_instance_transformation(1, object_name='obj', data={})
        assert resp.status_code == 200
        assert resp.json() == dict(foo='bar')



