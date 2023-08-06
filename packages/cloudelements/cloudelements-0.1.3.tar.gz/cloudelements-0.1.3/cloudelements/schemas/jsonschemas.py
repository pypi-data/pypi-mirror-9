string_schema = {
    'type': 'string',
    'maxLength': 255,
    'minLength': 1,
    'blank': False,
    'required': False
}

string_schema_allow_empty = {
    'type': 'string',
    'maxLength': 255,
    'blank': True,
    'required': False
}

array_of_strings_schema =  {
    'type': 'array',
    'uniqueItems': True,
    'items': [
        string_schema
    ],
    'required': False
}

string_schema_required  = {
    'type': 'string',
    'maxLength': 255,
    'minLength': 1,
    'blank': False,
    'required': True
}

boolean_schema = {
    'type': 'boolean',
    'required': False
}

integer_schema = {
    'type': 'integer',
    'minimum': 0,
    'required': False
}
create_lead_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'firstname': string_schema,
        'lastname': string_schema,
        'phone': string_schema,
        'description': string_schema,
        'leadsource': string_schema,
        'title': string_schema,
        'email': string_schema,
        'company': string_schema,
        'rating': string_schema,
        'postalcode': string_schema,
        'salutation': string_schema,
        'industry': string_schema,
        'street': string_schema,
        'status': string_schema,
        'isunreadbyowner':  boolean_schema,
        'city': string_schema,
        'state': string_schema,
        'country': string_schema,
        'fax': string_schema,
        'annualrevenue':  integer_schema
      }
}

contact_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'phone': string_schema,
        'email': string_schema,
        'firstname': string_schema,
        'lastname': string_schema_required,
        'department': string_schema,
        'mobilephone': string_schema,
        'title': string_schema,
        'lastmodifieddate': string_schema,
        'accountid': string_schema,
        'lastreferenceddate': string_schema,
        'salutation': string_schema,
        'name': string_schema,
        'createdbyid': string_schema,
        'ownerid': string_schema,
        'photourl': string_schema,
        'isdeleted': string_schema,
        'isemailbounced': string_schema,
        'hasoptedoutofemail': string_schema,
        'lastvieweddate': string_schema,
        'birthdate': string_schema,
        'systemmodstamp': string_schema,
        'leadsource': string_schema,
        'createddate': string_schema,
        'fax': string_schema,
        'lastmodifiedbyid': string_schema,
        'mailingstreet': string_schema
    }
}

lead_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        "firstname": string_schema,
        "lastname": string_schema_required,
        "phone": string_schema,
        "description": string_schema,
        "leadsource": string_schema,
        "title": string_schema,
        "email": string_schema,
        "company": string_schema_required,
        "rating": string_schema,
        "postalcode": string_schema,
        "salutation": string_schema,
        "industry": string_schema,
        "street": string_schema,
        "status": string_schema_required,
        "isunreadbyowner": boolean_schema,
        "city": string_schema,
        "state": string_schema,
        "country": string_schema,
        "fax": string_schema,
        "annualrevenue": integer_schema
    }
}

lead_schema_update = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        "firstname": string_schema,
        "lastname": string_schema,
        "phone": string_schema,
        "description": string_schema,
        "leadsource": string_schema,
        "title": string_schema,
        "email": string_schema,
        "company": string_schema,
        "rating": string_schema,
        "postalcode": string_schema,
        "salutation": string_schema,
        "industry": string_schema,
        "street": string_schema,
        "status": string_schema,
        "isunreadbyowner": boolean_schema,
        "city": string_schema,
        "state": string_schema,
        "country": string_schema,
        "fax": string_schema,
        "annualrevenue": integer_schema
    }
}

account_schema = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        "name": string_schema_required,
        "website": string_schema,
        "phone": string_schema,
        "billingstreet": string_schema,
        "billingcity": string_schema,
        "billingstate": string_schema,
        "billingpostalcode": string_schema,
        "billingcountry": string_schema,
        "type": string_schema,
        "annualrevenue": integer_schema,
        "numberofemployees": integer_schema,
        "description": string_schema,
        "shippingstreet": string_schema,
        "accountnumber": string_schema,
        "fax": string_schema,
        "rating": string_schema,
        "ownership": string_schema,
        "sic": string_schema,
        "industry":  string_schema
        }
}

instance_key_schema = {
    'enum': ['sfdc', 'sugar'],
    'required': False
}

instance_element_schema = {
    'type': 'object',
    'properties': {
            'id': integer_schema,
            'name': string_schema,
            'createdDate': integer_schema,
            'updatedDate': integer_schema,
            'key': instance_key_schema,
            'description': string_schema,
            'active': boolean_schema,
            'deleted': boolean_schema,
            'typeOauth': boolean_schema,
            'trialAccount': boolean_schema,
            'trialAccountDescription': string_schema,
            'existingAccountDescription': string_schema,
            'configDescription':  string_schema,
            'signupURL': string_schema,
            'authenticationType': string_schema,
            'hub': string_schema,
            'transformationsEnabled': boolean_schema
          }
}

instance_provision_schema = {
    "type": "object",
    "properties": {
        "maxcachesize": integer_schema,
        "element":  instance_element_schema,
        "providerData": {
            "type": "object",
            "properties": {
                "code": string_schema,
            },
            'required': False
        },
        "configuration": {
            "type": 'object',
            'properties': {
                "oauth.callback.url": string_schema,
                "oauth.api.key": string_schema,
                "oauth.api.secret": string_schema
            },
            'required': False
        },
        "tags": string_schema_allow_empty,
        "name": string_schema,
        "valid": boolean_schema,
        "channelname": string_schema,
        "updateddate": integer_schema,
        "id": integer_schema,
        "cachetimetolive": integer_schema,
        "token": string_schema,
        "description": string_schema,
        "cachingenabled": boolean_schema,
        "createddate": integer_schema,
        "disabled": boolean_schema
    }
}
