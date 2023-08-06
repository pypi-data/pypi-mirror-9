Python Bindings for CloudCIX API
================================

Python bindings and utils to make the work with CloudCIX API fun.

API Docs: http://docs.cloudcix.com

CloudCIX is developed by CIX: http://www.cix.ie

Installation
============

::

    pip install cloudcix

Required settings
=================

When you run your project you should set the settings variable
``CLOUDCIX_SETTINGS_MODULE`` to point to the module that contains the
settings object.

Example django lazy settings object (object should be specified after
":"):

::

    import os
    os.environ.setdefault("CLOUDCIX_SETTINGS_MODULE", "django.conf:settings")

Example for a module based settings:

::

    import os
    os.environ.setdefault("CLOUDCIX_SETTINGS_MODULE", "my.project.my_settings")

Required ``CLOUDCIX`` and ``OPENSTACK`` settings

::

    CLOUDCIX_SERVER_URL = 'https://api.cloudcix.com'
    CLOUDCIX_API_USERNAME = 'user@cloudcix.com'
    CLOUDCIX_API_PASSWORD = 'super53cr3t3'
    CLOUDCIX_API_ID_MEMBER = '2243'
    OPENSTACK_KEYSTONE_URL = 'http://keystone.cloudcix.com:5000/v3'

As an alternative when used from console the settings can be set as
environment variables

::

    os.environ['CLOUDCIX_SERVER_URL'] = 'https://api.cloudcix.com/'

utils method get\_admin\_token and get\_admin\_session, will require you
to set following environment variables as well

::

    os.environ['CLOUDCIX_API_USERNAME'] = 'user@cloudcix.com'
    os.environ['CLOUDCIX_API_PASSWORD'] = 'super53cr3t3'
    os.environ['CLOUDCIX_API_ID_MEMBER'] = '2243'
    os.environ['OPENSTACK_KEYSTONE_URL'] = 'http://keystone.cloudcix.com:5000/v3'

Sample usage
============

Use the language service
------------------------

::

    from cloudcix import api
    from cloudcix.utils import get_admin_session

    # get an admin token
    token = get_admin_session().get_token()

    # call a sample membership service
    api.membership.language.list()

Create token for a User, and read the User Address
--------------------------------------------------

::

    from cloudcix import api
    from cloudcix.cloudcixauth import CloudCIXAuth
    from cloudcix.utils import KeystoneSession, KeystoneClient, \
        get_admin_client
    from keystoneclient.exceptions import NotFound

    # create auth payload
    auth = CloudCIXAuth(
        auth_url=settings.OPENSTACK_KEYSTONE_URL,
        username='john@doe.com',
        password='ubersecret',
        idMember='2243')
    auth_session = KeystoneSession(auth=auth)
    user_token = auth_session.get_token()
    token_data = auth_session.auth.auth_ref

    # for the sake of example check that the token is valid
    # you should use your admin credentials to check user's token
    admin_cli = get_admin_client()
    try:
        admin_cli.tokens.validate(user_token)
    except NotFound as e:
        # Token is invalid, re-raise the exception
        raise e
    # token is valid, continue

    # Finally, read the address
    response = api.membership.address.read(
        pk=token_data['user']['address']['idAddress'],
        token=user_token)

    # check the response status to ensure we've been able to read the address
    if response.status_code != 200:
        # we couldn't read the address
        return response.content

    address = response.json()['content']

    # Finally delete the token
    admin_cli.tokens.revoke_token(user_token)

    # And make sure it's not longer valid
    try:
        admin_cli.tokens.validate(user_token)
    except NotFound as e:
        # Token is not longer valid
        pass

Given an expiring token, get a new token for further calls
----------------------------------------------------------

::

    from cloudcix.utils import KeystoneTokenAuth, KeystoneSession

    expiring_token = 'xyz123'
    auth = KeystoneTokenAuth(
        auth_url=settings.OPENSTACK_KEYSTONE_URL,
        token=expiring_token)
    new_token = KeystoneSession(auth=auth).get_token()
