import pytest
import unittest

from mock import patch, MagicMock, PropertyMock
from contextlib import nested


class TestCloudElements(unittest.TestCase):
    def setUp(self):
        import os
        from cloudelements import CloudElements

        self.user_secret = os.getenv('CLOUD_ELEMENTS_USER_SECRET')
        self.org_secret = os.getenv('CLOUD_ELEMENTS_ORG_SECRET')
        self.sales_force_secret = os.getenv('SALES_FORCE_SECRET')
        self.sales_force_access_key = os.getenv('SALES_FORCE_ACCESS_KEY')
        self.sales_force_callback = os.getenv('SALES_FORCE_CALLBACK_URL')

        self.cloud_elements = CloudElements(
            user_secret=self.user_secret,
            org_secret=self.org_secret
        )


class TestHub(TestCloudElements):

    def test_get_hubs(self):
        resp = self.cloud_elements.get_hubs()
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        crm = False
        for hub in hubs:
            if 'crm' == hub['key']:
                crm = True
                break
        assert crm is True

    def test_hubs_keys(self):
        resp = self.cloud_elements.get_hubs_keys()
        assert resp is not None
        assert resp.status_code == 200
        hubs = resp.json()
        assert type(hubs) == list
        assert 'crm' in hubs

    def test_get_hub_key(self):
        resp = self.cloud_elements.get_hub_key('crm')
        assert resp is not None
        assert resp.status_code == 200
        assert resp.json() == \
            {
                "id": 11,
                "name": "CRM",
                "key": "crm",
                "description": "CRM Element Hub",
                "videoLink": "//player.vimeo.com/video/113632224?title=0&amp;byline=0&amp;portrait=0&amp;autoplay=1",
                "active": True
            }

    def test_get_hub_key_for_elements(self):
        resp = self.cloud_elements.get_hub_key_for_elements('crm')
        assert resp is not None
        assert resp.status_code == 200
        assert type(resp.json()) == list
        elements = resp.json()
        sfdc = False
        for element in elements:
            if 'sfdc' == element['key']:
                sfdc = True
                break
        assert sfdc is True


class TestInstances(TestCloudElements):
    def test_get_sales_force_provision_url(self):
        resp = self.cloud_elements.get_sales_force_provision_url(
            key=self.sales_force_access_key,
            secret=self.sales_force_secret,
            callback_url=self.sales_force_callback
        )

        assert resp.status_code == 200
        assert 'oauthUrl' in resp.json()
        # And its for this reason, PEP8 Rules suck
        assert resp.json() == \
            {
                'oauthUrl':  'https://login.salesforce.com/services/'
                    'oauth2/authorize?response_type=code&'
                    'client_id={key}&client_secret={secret}'
                    '&scope=full%20refresh_token'
                    '&redirect_uri={callback}'
                    '&state=sfdc'
                    .format(
                        key=self.sales_force_access_key,
                        secret=self.sales_force_secret,
                        callback=self.sales_force_callback,
                    ),
                'element':  'sfdc'
            }

    def test_get_instances(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        assert resp.json() is not None
        assert type(resp.json()) == list

    def test_get_instance(self):
        # need to create an instance
        resp = self.cloud_elements.get_instances()
        assert resp is not None
        instance = resp.json().pop()
        resp = self.cloud_elements.get_instance(instance['id'])

        assert resp is not None
        assert resp.status_code == 200

    """
    def test_provision_sales_force_instance(self):
        import random
        name = 'test_instance_%s' % random.randint(0, 1000)
        resp = self.cloud_elements.provision_sales_force_instance(
            key=self.sales_force_access_key,
            secret=self.sales_force_secret,
            callback_url='http://localhost',
            name=name,
            code='adfasdfadfsdafsadfsadfsaf'
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 'id' in data
        assert data['name'] == name
        assert data['id'] is not None

        #delete instance
        #resp = self.cloud_elements.delete_instance(instance_id=data['id'])
        #assert resp.status_code == 200
    """


class TestCRMHub(TestCloudElements):

    def test_get_crm_accounts(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        instances = resp.json()
        instance = instances.pop()
        self.cloud_elements.element_token = instance['token']
        resp = self.cloud_elements.get_crm_accounts(query="name like 'Chris'")
        assert resp is not None
        assert type(resp.json()) == list

    def test_crm_account(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        instances = resp.json()
        assert len(instances) > 0
        instance = instances[0]
        self.cloud_elements.element_token = instance['token']

        resp = self.cloud_elements.create_crm_accounts(data={
            'name': 'Chris George'
        })
        assert resp.status_code == 200
        account = resp.json()
        acct_id = account['Id']
        assert acct_id is not None
        assert account['name'] == 'Chris George'

        resp = self.cloud_elements.update_crm_account_by_id(
            acct_id=acct_id,
            data={'name': 'Test'}
        )

        assert resp is not None
        assert resp.status_code == 200
        assert resp.json()['name'] == 'Test'

        resp = self.cloud_elements. \
            delete_crm_account_by_id(acct_id=account['Id'])

        assert resp.status_code == 200

        # fail getting it
        resp = self.cloud_elements.get_crm_account_by_id(acct_id=acct_id)
        assert resp.status_code == 404

    def test_crm_contacts(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        instances = resp.json()
        assert len(instances) > 0
        instance = instances[0]
        self.cloud_elements.element_token = instance['token']

        resp = self.cloud_elements.get_crm_contacts(query='name like "chris"')
        resp.status_code == 200
        assert resp.json() is not None
        assert type(resp.json()) == list

        resp = self.cloud_elements.create_crm_contact({'lastname': 'foo'})
        assert resp.status_code == 200
        contact = resp.json()

        acct_id = contact['Id']
        assert acct_id is not None
        assert contact['lastname'] == 'foo'

        resp = self.cloud_elements.update_crm_contact(
            contact_id=acct_id,
            data={'lastname': 'Test'}
        )

        assert resp is not None
        assert resp.status_code == 200
        assert resp.json()['lastname'] == 'Test'

        resp = self.cloud_elements. \
            delete_crm_contact(contact_id=acct_id)

        assert resp.status_code == 200

    def test_crm_leads(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        instances = resp.json()
        assert len(instances) > 0
        instance = instances[0]

        self.cloud_elements.element_token = instance['token']
        resp = self.cloud_elements.get_crm_leads(query='firstname is not null')
        resp.status_code == 200
        assert resp.json() is not None
        assert type(resp.json()) == list

        # test with pagination
        resp = self.cloud_elements.\
            get_crm_leads(query='firstname is not null', page=0, page_size=5)
        assert resp.status_code == 200
        assert 'elements-returned-count' in resp.headers.keys()
        assert 'elements-total-count' in resp.headers.keys()
        assert int(resp.headers.get('elements-returned-count')) == 5
        leads = resp.json()
        assert len(leads) == 5

        resp = self.cloud_elements.\
            create_crm_lead(data={
                'lastname': 'foo',
                'status': 'somestatus',
                'company': 'Foo'
            })
        assert resp.status_code == 200
        assert resp.json() is not None
        assert resp.json()['lastname'] == 'foo'

        lead = resp.json()
        lead_id = lead['Id']
        resp = self.cloud_elements.\
            update_crm_lead(lead_id=lead_id, data={'lastname': 'Test'})

        assert resp is not None
        assert resp.json()['lastname'] == 'Test'

        resp = self.cloud_elements.delete_crm_lead(lead_id=lead_id)

        assert resp.status_code == 200

    def test_crm_instances(self):
        resp = self.cloud_elements.get_instances()
        assert resp.status_code == 200
        instances = resp.json()
        assert len(instances) > 0
        instance = instances[0]

        instance_id  = instance['id']
        resp = self.cloud_elements.get_instance(instance_id)
        assert resp.status_code == 200
        assert resp.json()['id'] == instance_id


class TestElements(TestCloudElements):
    def test_get_all_elements(self):
        resp = self.cloud_elements.get_all_elements()
        assert resp is not None
        assert resp.status_code == 200
        assert type(resp.json()) == list

    def test_get_all_element_keys(self):
        resp = self.cloud_elements.get_all_element_keys()

        assert resp is not None
        assert resp.status_code == 200
        keys = resp.json()
        assert type(keys) == list
        assert 'sfdc' in keys
        assert 'sugar' in keys

    def test_get_element_config_by_key(self):
        resp = self.cloud_elements.get_element_config_by_key('sfdc')
        assert resp is not None
        assert resp.status_code == 200
        keys = resp.json()
        assert 'configuration' in keys
        assert type(keys['configuration']) == list

    def test_get_sales_force_provision_url(self):
        resp = self.cloud_elements.get_sales_force_provision_url(
            key=self.sales_force_access_key,
            secret=self.sales_force_secret,
            callback_url='http://localhost'
        )
        assert resp is not None
        assert resp.status_code == 200

        assert resp.json()['element'] == 'sfdc'


