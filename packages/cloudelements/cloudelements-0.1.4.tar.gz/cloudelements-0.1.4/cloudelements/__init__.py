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
    headers  = {}

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
        headers = kwargs.get('headers' , self.headers)

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
        auth_token_template = "User {user_secret}, " \
                                    "Organization {org_secret}"
        element_template = ', Element: {element_token}'

        post_headers = {
            "Content-type": "application/json",
            "Accept":  "application/json",
            "Connection": "close",
        }

        paths = {
            'accounts': '/hubs/crm/accounts',
            'leads': '/hubs/crm/leads',
            'contacts': '/hubs/crm/contacts',
            'bulk': '/hubs/crm/bulk',
            'element': '/elements',
            'instances': '/instances',
            'elements': '/elements'
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
                    auth_header + self.element_template.format(element_token=self.element_token)
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
            params = kwargs.get('params')

            return self._send_request(
                url=url,
                data=json.dumps(data),
                method='POST',
                headers=headers,
                params=params,
                **kwargs
            )

        def get_crm_accounts(self,  query):
            """ /hubs/crm/accounts GET """
            params = {
                'where': query
            }
            return self._get(self.paths['accounts'], params=params)

        @validate_schema(schema=account_schema)
        def create_crm_accounts(self, data):
            """ /hubs/crm/accounts POST """
            return self._post(self.paths['accounts'], data=data)

        def get_crm_account_by_id(self, acct_id):
            """ /hubs/crm/accounts/{id} GET """
            url = "%s/%s" % (
                self.paths['accounts'],
                acct_id
            )

            return self._get(url)

        @validate_schema(schema=account_schema)
        def update_crm_account_by_id(self, acct_id, data):
            """ /hubs/crm/accounts/{id} PATCH """
            url = "%s/%s" % (
                self.paths['accounts'],
                acct_id
            )

            return self._patch(url, data=data)

        def delete_crm_account_by_id(self, acct_id):
            """ /hubs/crm/accounts/{id} DELETE """
            url = "%s/%s" % (
                self.paths['accounts'],
                acct_id
            )

            return self._delete(url)

        def bulk_crm_query():
            """ /hubs/crm/bulk/query GET """
            pass

        def get_crm_bulk_job_status(self, jobid):
            """ /hubs/crm/bulk/{id}/status GET """
            pass

        def get_crm_bulk_job_errors(self, jobid):
            """ /hubs/crm/bulk/{id}/errors GET """
            pass

        def get_crm_bulk_job_object(self, jobid, object_name):
            """ /hubs/crm/bulk/{id}/{object_name} GET """
            pass

        def upload_crm_bulk(self, object_name, data):
            """
                /hubs/crm/bulk/{object_name} POST
                Bulk upload of file objects to object_name
            """
            pass

        @validate_schema(schema=contact_schema)
        def create_crm_contact(self, data):
            """ /hubs/crm/contacts POST """
            url = self.paths['contacts']
            return self._post(url, data=data)

        def get_crm_contact(self, contact_id):
            """ /hubs/crm/contacts/{id} GET """
            url = '%s/%s' % (self.paths['contacts'], contact_id)
            return self._get(url)

        def get_crm_contacts(self, query):
            """ /hubs/crm/contacts GET """
            params = {
                'query': query
            }

            return self._get(self.paths['contacts'], params=params)

        @validate_schema(schema=contact_schema)
        def update_crm_contact(self, contact_id, data):
            """ /hubs/crm/contacts/{id} PATCH """
            url = '%s/%s'  % (self.paths['contacts'], contact_id)

            return self._patch(url, data=data)

        def delete_crm_contact(self, contact_id):
            """ /hubs/crm/contacts/{id} DELETE """
            url = '%s/%s'  % (self.paths['contacts'], contact_id)

            return self._delete(url)

        def get_crm_leads(self, query):
            """ /hubs/crm/leads GET """
            params = {
                'query': query
            }

            return self._get(self.paths['leads'], params=params)

        @validate_schema(schema=lead_schema)
        def create_crm_lead(self, data):
            """ /hubs/crm/leads POST """

            return self._post(self.paths['leads'], data=data)

        def get_crm_lead(self, lead_id):
            """ /hubs/crm/leads/{id} GET """
            url = '%s/%s' % (self.paths['leads'], lead_id)

            return self._get(url)

        @validate_schema(schema=lead_schema_update)
        def update_crm_lead(self, lead_id, data):
            """ /hubs/crm/leads/{id} PATCH """
            url = '%s/%s' % (self.paths['leads'], lead_id)

            return self._patch(url, data=data)

        def delete_crm_lead(self, lead_id):
            """ /hubs/crm/leads/{id} DELETE """
            url = '%s/%s' % (self.paths['leads'], lead_id)

            return self._delete(url)

        def get_sales_force_provision_url(self, key, secret, callback_url):
            """ /elements/{key}/oauth/url GET
                returns:
                {
                    "oauthUrl": url,
                    "element": element name,
                }
            """
            url =  '/elements/sfdc/oauth/url'
            params = {
                'apiKey': key,
                'apiSecret': secret,
                'callbackUrl': callback_url
            }

            return self._get(url, params=params)

        def provision_sales_force_instance(self, key, secret, callback_url, name, code, **kwargs):
            """ Convenience specific to creating sales force instances """
            tags = kwargs.get('tags')

            """
                returns:
                {
                    "id": 11,
                    "name": "api-v2 provisioning",
                    "token": "3sU/S/kZD36BaABPS7EAuSGHF+1wsthT+mvoukiE",
                    "element": {
                        "id": 39,
                        "name": "Salesforce.com",
                        "key": "sfdc",
                        "description": "The Salesforce.com allows you to deliver revolutionary CRM automation functionality, such as account and contact creation, from anywhere, anytime, on any device.",
                        "active": true,
                        "deleted": false,
                        "typeOauth": true,
                        "trialAccount": false,
                        "configDescription": "If you do not have a Salesforce.com account, you can create one at <a href="http://www.salesforce.com" target="_blank">Salesforce.com Signup</a>",
                        "signupURL": "http://www.salesforce.com"
                    },
                    "provisionInteractions": [],
                    "valid": true,
                    "disabled": false,
                    "maxCacheSize": 0,
                    "cacheTimeToLive": 0,
                    "cachingEnabled": false
                }
            """
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

        def delete_instance(self, instance_id):
            """ /instances/{id} DELETE """
            url = '%s/%s' % (self.paths['instances'], id)
            return self._delete(self.paths['instances'])

        def get_instances(self):
            """ /instances GET """

            return self._get(self.paths['instances'])

        def get_instance(self, instance_id):
            """ /instances/{id} GET """

            url = "%s/%s" % (self.paths['instances'], instance_id)
            return self._get(url)

        #TODO opportunities, objects, users
