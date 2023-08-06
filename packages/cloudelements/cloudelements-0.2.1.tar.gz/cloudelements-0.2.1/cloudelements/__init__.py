import logging
import json
import requests
import time
import os

from requests.exceptions import *

from cloudelements.schemas.jsonschemas import *
from cloudelements.validation import validate_schema

if os.getenv('DEBUG', False) and os.path.isfile('dev_logging.conf'):
    from logging.config import dictConfig
    dictConfig(
        json.loads(open('dev_logging.conf').read())
    )

log = logging.getLogger(__name__)

DEFAULT_PAGE = 0
DEFAULT_PAGE_SIZE = 200

def _log_info(path, status, data, request_type, headers, chrono,  exception=None):
    if exception:
        log.error(
            "[CloudElements] "
            "path=%(url)s "
            " http_status=%(http_status)s "
            "error=%(error)s "
            "request_type=%(request_type)s "
            "post=%(post)s "
            "ms=%(ms).0f", {
                "url": path,
                "http_status": status,
                "error": exception,
                "post": data,
                "ms": chrono,
                "request_type": request_type
            }
        )

    else:
        log.info(
            "[CloudElements] \
             path=%(url)s \
             http_status=%(http_status)s \
             request_type=%(request_type)s \
             post=%(post)s \
             ms=%(ms).0f", {
                "url": path,
                "http_status": status,
                "post": data,
                "ms": chrono,
                "request_type": request_type
            }
        )


class BaseRequest(object):
    """ BaseRequest Object for Resources
    """
    base_url = ''
    headers = {}

    def __init__(self, base_url=None):
        """ Initialization function for BaseRequest """
        self.base_url = base_url or self.base_url

    def _send_request(self, url, method='GET', **kwargs):
        """ Base send method for request """
        headers = self.headers.copy()
        headers.update(kwargs.get('headers', {}))
        params = kwargs.get('params', None)
        data = kwargs.get('data', None)
        url = '%s%s' % (self.base_url, url)

        exception = None
        chrono = time.time()
        status = None
        response = None

        try:
            method = method.upper()
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(
                    url=url,
                    data=data,
                    headers=headers
                )
            elif method == 'DELETE':
                response = requests.delete(
                    url=url,
                    params=params,
                    headers=headers
                )
            elif method == 'PUT':
                response = requests.put(
                    url=url,
                    params=params,
                    headers=headers,
                    data=data
                )
            elif method == 'PATCH':
                response = requests.patch(
                    url=url,
                    params=params,
                    headers=headers,
                    data=data
                )
            else:
                raise Exception("Method not found.")

        except Exception as exc:
            exception = exc

        chrono = (time.time() - chrono) * 1000  # ms
        _log_info(
            path=url,
            status=status,
            data=data or None,
            request_type=method,
            headers=headers,
            chrono=chrono,
            exception=exception
        )

        return response

    def _post(self, url, data, **kwargs):
        params = kwargs.get('params')
        headers = kwargs.get('headers', self.headers)

        return self._send_request(
            url=url,
            data=data,
            method='POST',
            headers=headers,
            params=params,
            **kwargs
        )

    def _get(self, url, params=None, **kwargs):
        headers = kwargs.get('headers', {})

        return self._send_request(
            url=url,
            method='GET',
            params=params,
            headers=headers,
            **kwargs
        )

    def _put(self, url, data, **kwargs):
        headers = kwargs.get('headers', self.headers)
        params = kwargs.get('params')

        return self._send_request(
            url=url,
            method='PUT',
            data=data,
            params=params,
            headers=headers,
            **kwargs
        )

    def _patch(self, url, data, **kwargs):
        headers = kwargs.get('headers', self.headers)
        params = kwargs.get('params')

        return self._send_request(
            url=url,
            method='PATCH',
            data=data,
            params=params,
            headers=headers,
            **kwargs
        )

    def _delete(self, url, **kwargs):
        headers = kwargs.get('headers', {})
        params = kwargs.get('params')

        return self._send_request(
            url=url,
            method='DELETE',
            params=params,
            headers=headers,
            **kwargs
        )


class CloudElements(BaseRequest):
    base_url = 'https://api.cloud-elements.com/elements/api-v2'
    auth_token_template = \
        "User {user_secret}, " \
        "Organization {org_secret}"
    element_template = ', Element: {element_token}'

    post_headers = {
        "Content-type": "application/json",
        "Accept":  "application/json",
        "Connection": "close",
    }

    paths = {
        # CRM Paths
        'accounts_crm': '/hubs/crm/accounts',
        'leads_crm': '/hubs/crm/leads',
        'contacts_crm': '/hubs/crm/contacts',
        'bulk_crm': '/hubs/crm/bulk',
        # Instances Path
        'instances': '/instances',
        # Elements Path
        'elements': '/elements',
        # Hub Path
        'hubs': '/hubs',
        # Users Path
    }

    def __init__(self, user_secret, org_secret, element_token=None):
        super(CloudElements, self).__init__()
        self.user_secret = user_secret
        self.org_secret = org_secret
        self.element_token = element_token

    def _send_request(self, url, method='GET', **kwargs):
        auth_header = self.auth_token_template. \
            format(user_secret=self.user_secret, org_secret=self.org_secret)

        if self.element_token:
            log.debug('[event=send_request] Adding element token.')
            auth_header = \
                auth_header + \
                self.element_template.format(element_token=self.element_token)

            log.debug('Auth header is: %s', auth_header)

        kwargs['headers']['Authorization'] = auth_header
        # Oh so hacky.
        return super(CloudElements, self)._send_request(url, method, **kwargs)

    def _patch(self, url, data, **kwargs):
        headers = self.headers.copy()
        headers.update(self.post_headers)
        headers.update(kwargs.get('headers', {}))
        params = kwargs.get('params')

        return self._send_request(
            url=url,
            data=json.dumps(data),
            method='PATCH',
            headers=headers,
            params=params,
            **kwargs
        )

    def _post(self, url, data, **kwargs):
        headers = self.headers.copy()
        headers.update(self.post_headers)
        headers.update(kwargs.get('headers', {}))

        return self._send_request(
            url=url,
            data=json.dumps(data),
            method='POST',
            headers=headers,
            **kwargs
        )

    ################
    # HUB Methods
    ################
    def get_hubs(self):
        """ /hubs GET
            Retrieves all hub types CloudElements Supports
        """

        return self._get(self.paths['hubs'])

    def get_hubs_keys(self):
        """ /hubs/keys GET """
        return self._get('%s/keys' % self.paths['hubs'])

    def get_hub_key(self, key):
        """ /hubs/{key} GET """
        return self._get('%s/%s' % (self.paths['hubs'], key))

    def get_hub_key_for_elements(self, key):
        """ /hubs/{key}/elements GET """
        return self._get(
            '%s/%s/elements' % (self.paths['hubs'], key)
        )

    ##################
    # CRM HUB Methods
    ##################
    def get_crm_accounts(self,  query, page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE):
        """ /hubs/crm/accounts GET """
        params = {
            'where': query,
            'page': page,
            'pageSize': page_size,
            'returnTotalCount': True # if we're paginating, always get the total.
        }

        return self._get(self.paths['accounts_crm'], params=params)

    @validate_schema(schema=account_schema)
    def create_crm_accounts(self, data):
        """ /hubs/crm/accounts POST """
        return self._post(self.paths['accounts_crm'], data=data)

    def get_crm_account_by_id(self, acct_id):
        """ /hubs/crm/accounts/{id} GET """
        url = "%s/%s" % (
            self.paths['accounts_crm'],
            acct_id
        )

        return self._get(url)

    @validate_schema(schema=account_schema)
    def update_crm_account_by_id(self, acct_id, data):
        """ /hubs/crm/accounts/{id} PATCH """
        url = "%s/%s" % (
            self.paths['accounts_crm'],
            acct_id
        )

        return self._patch(url, data=data)

    def delete_crm_account_by_id(self, acct_id):
        """ /hubs/crm/accounts/{id} DELETE """
        url = "%s/%s" % (
            self.paths['accounts_crm'],
            acct_id
        )

        return self._delete(url)

    def create_crm_bulk_job(self, query):
        """
            /hubs/crm/bulk/query POST
            Asynchronous Bulk Query Job
        """
        return self._post(
            '%s/query' % self.paths['bulk_crm'],
            data=None,
            params={
                'q': query
            }
        )

    def bulk_crm_query(self, query):
        """
            /hubs/crm/bulk/query GET
            Synchronous bulk query job
        """
        return self._get(
            '%s/query' % self.paths['bulk_crm'],
            params={
                'q': query
            }
        )

    def get_crm_bulk_job_status(self, job_id):
        """ /hubs/crm/bulk/{id}/status GET """
        return self._get(
            '%s/%s/status' %
            (self.paths['bulk_crm'], job_id)
        )

    def get_crm_bulk_job_errors(self, job_id):
        """ /hubs/crm/bulk/{id}/errors GET """
        return self._get(
            '%s/%s/errors' % (self.paths['bulk_crm'], job_id)
        )

    def get_crm_bulk_job_object(self, job_id, object_name):
        """ /hubs/crm/bulk/{id}/{object_name} GET """
        return self._get(
            '%s/%s/%s' %
            (self.paths['bulk_crm'], job_id, object_name)
        )

    def create_crm_bulk_objects(self, object_name, identitifer, file_upload):
        """ /bulk/{objectName} POST """
        pass

    @validate_schema(schema=contact_schema)
    def create_crm_contact(self, data):
        """ /hubs/crm/contacts POST """
        url = self.paths['contacts_crm']
        return self._post(url, data=data)

    def get_crm_contact(self, contact_id):
        """ /hubs/crm/contacts/{id} GET """
        url = '%s/%s' % (self.paths['contacts_crm'], contact_id)
        return self._get(url)

    def get_crm_contacts(self, query, page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE):
        """ /hubs/crm/contacts GET """
        params = {
            'query': query,
            'page': DEFAULT_PAGE,
            'pageSize': DEFAULT_PAGE_SIZE,
            'returnTotalCount': True # if we're paginating, always get the total.
        }

        return self._get(self.paths['contacts_crm'], params=params)

    @validate_schema(schema=contact_schema)
    def update_crm_contact(self, contact_id, data):
        """ /hubs/crm/contacts/{id} PATCH """
        url = '%s/%s' % (self.paths['contacts_crm'], contact_id)

        return self._patch(url, data=data)

    def delete_crm_contact(self, contact_id):
        """ /hubs/crm/contacts/{id} DELETE """
        url = '%s/%s' % (self.paths['contacts_crm'], contact_id)

        return self._delete(url)

    def get_crm_leads(self, query, page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE):
        """ /hubs/crm/leads GET
            `Pagination`:
                Elements-Returned-Count
                Elements-Total-Count
        """
        params = {
            'query': query,
            'page': page,
            'pageSize': page_size,
            'returnTotalCount': True # if we're paginating, always get the total.
        }

        return self._get(self.paths['leads_crm'], params=params)

    @validate_schema(schema=lead_schema)
    def create_crm_lead(self, data):
        """ /hubs/crm/leads POST """

        return self._post(self.paths['leads_crm'], data=data)

    def get_crm_lead(self, lead_id):
        """ /hubs/crm/leads/{id} GET """
        url = '%s/%s' % (self.paths['leads_crm'], lead_id)

        return self._get(url)

    @validate_schema(schema=lead_schema_update)
    def update_crm_lead(self, lead_id, data):
        """ /hubs/crm/leads/{id} PATCH """
        url = '%s/%s' % (self.paths['leads_crm'], lead_id)

        return self._patch(url, data=data)

    def delete_crm_lead(self, lead_id):
        """ /hubs/crm/leads/{id} DELETE """
        url = '%s/%s' % (self.paths['leads_crm'], lead_id)

        return self._delete(url)

    ###############
    # Elements API
    ###############
    def get_all_elements(self):
        """ /elements GET """
        return self._get(self.paths['elements'])

    def get_all_element_keys(self):
        """ /elements/keys GET """
        return self._get('%s/keys' % self.paths['elements'])

    def get_element_by_key(self, key):
        """ /elements/{key} GET """
        return self._get('%s/%s' % (self.paths['elements'], key))

    def get_element_config_by_key(self, key):
        """ /elements/{key}/configuration GET """
        return self._get(
            '%s/%s/configuration' % (self.paths['elements'], key)
        )

    def get_element_oauth_token(self, key, **kwargs):
        """ /elements/{key}/oauth/token GET """
        return self._get(
            '%s/%s/oauth/token' % (self.paths['elements'], key),
            **kwargs
        )

    def get_element_oauth_url(self, key, **kwargs):
        """ /elements/{key}/oauth/url GET """

        return self._get(
            '%s/%s/oauth/url' % (self.paths['elements'], key),
            **kwargs
        )

    def get_sales_force_provision_url(self, key, secret, callback_url):
        """ Convenience method to provision SalesForce oauth URLs.
            /elements/{key}/oautTh/url GET
            returns:
            {
                "oauthUrl": url,
                "element": element name,
            }
        """
        params = {
            'apiKey': key,
            'apiSecret': secret,
            'callbackUrl': callback_url
        }

        return self.get_element_oauth_url(key='sfdc', params=params)

    #################
    # Instances API
    #################
    def provision_sales_force_instance(self, key, secret, callback_url, name, code, **kwargs):
        """ Convenience method specific to creating sales force instances """
        tags = kwargs.get('tags')
        data = {
            'element': {
                'key': 'sfdc'
            },
            'configuration': {
                "oauth.callback.url": callback_url,
                "oauth.api.key": key,
                "oauth.api.secret": secret
            },
            'name': name,
            'providerData': {
                'code': code
            }
        }

        if tags is not None:
            data['tags'] = tags

        return self._provision_instance(data)

    @validate_schema(schema=instance_provision_schema)
    def _provision_instance(self, data):
        """ /instances POST """

        return self._post('/instances', data=data)

    def get_instances(self):
        """ /instances GET """

        return self._get(self.paths['instances'])

    def get_instance(self, instance_id):
        """ /instances/{id} GET """

        url = "%s/%s" % (self.paths['instances'], instance_id)
        return self._get(url)

    def delete_instance(self, instance_id):
        """ /instances/{id} DELETE """
        url = '%s/%s' % (self.paths['instances'], instance_id)
        return self._delete(url)

    @validate_schema(schema=instance_provision_schema)
    def update_instance(self, instance_id, data):
        """ /instances/{id} PUT

        NOTE: this is inconsistent with using ```PATCH```
            as the method for updating in a REST API.
        """

        return self._put(
            '%s/%s' % (self.paths['instances'], instance_id),
            data=data
        )

    def create_instance(self, data):
        """ /instances POST
            This function assumes you know
            what dataset is needed for any given
            instance.
        """
        return self._provision_instance(data)

    def get_instance_transformations(self, instance_id):
        """ /instances/{id}/transformations GET """

        return self._get(
            '%s/%s/transformations' % (self.paths['instances'], instance_id)
        )

    def delete_instance_transformations(self, instance_id):
        """ /instances/{id}/transformations DELETE """

        return self._delete(
            '%s/%s/transformations'
            % (self.paths['instances'], instance_id)
        )

    def create_instance_transformation(self, instance_id, object_name, data):
        """ /instances/{id}/transformations/{objectName} POST """

        return self._post(
            "%s/%s/transformations/%s" % (
                self.paths['instances'],
                instance_id,
                object_name
            ),
            data=data
        )

    def get_instance_transformation(self, instance_id, object_name):
        """ /instances/{id}/transformatinos/{objectName} GET """
        return self._get(
            "%s/%s/transformations/%s" % (
                self.paths['instances'],
                instance_id,
                object_name
            )
        )

    def delete_instance_transformation(self, instance_id, object_name):
        """ /instances/{id}/transformatinos/{objectName} DELETE """
        return self._delete(
            "%s/%s/transformations/%s" % (
                self.paths['instances'],
                instance_id,
                object_name
            )
        )

    def update_instance_transformation(self, instance_id, object_name, data):
        """ /instances/{id}/transformatinos/{objectName} PUT """
        return self._put(
            "%s/%s/transformations/%s" % (
                self.paths['instances'],
                instance_id,
                object_name
            ),
            data=data
        )
