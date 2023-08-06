CLOUD ELEMENTS PYTHON SDK
==========================

[![Build Status](https://travis-ci.org/MobileWorks/cloudelements.svg)](https://travis-ci.org/MobileWorks/cloudelements) [![Coverage Status](https://coveralls.io/repos/MobileWorks/cloudelements/badge.svg?branch=master)](https://coveralls.io/r/MobileWorks/cloudelements?branch=master) [![Join the chat at https://gitter.im/MobileWorks/cloudelements](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/MobileWorks/cloudelements?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This SDK is a basic wrapper around the HTTP/S calls needed to use CloudElements

Current Version: 0.2
------

v0.2.1
----
* Add pagination for CRM Hubs

v0.2
----
* More complete coverage for the CE API including CRM hubs, instances, elements, and providers
* Updated test cover
* More consistent naming conventions
* Group tests via "type"

v0.1
-----
* Mostly SalesForce and CRM Hub integration


##INSTALLATION
```shell
    git clone git@github.com:MobileWorks/cloudelements.git cloudelements
    cd cloudelements
    pip install -e .
    pip install -r test-requirements.txt
```

## SETUP
Instead of having set variables in the file, the tests rely on environment variables for your instances.

You can use a tool like [direnv](https://github.com/zimbatm/direnv/) or [autoenv](https://github.com/kennethreitz/autoenv)

Currently the tests use these:

```python
    os.getenv('CLOUD_ELEMENTS_USER_SECRET')
    os.getenv('CLOUD_ELEMENTS_ORG_SECRET')
    os.getenv('SALES_FORCE_SECRET')
    os.getenv('SALES_FORCE_ACCESS_KEY')
    os.getenv('SALES_FORCE_CALLBACK_URL')
```
## RUN TESTS
``` py.test -v ```

OR

```shell
    pip install tox
    tox .
```

