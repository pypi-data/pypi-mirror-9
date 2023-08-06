# python
from __future__ import unicode_literals
import importlib
import os

# libs
from keystoneclient.session import Session as KeystoneSession
from keystoneclient.v3.client import Client as KeystoneClient

# local
from .cloudcixauth import CloudCIXAuth

__all__ = ['KeystoneSession', 'KeystoneClient', 'settings',
           'get_admin_session', 'get_admin_client']


def new_method_proxy(func):
    """When attribute is accessed in lazy object, this method makes sure that
    lazy object was properly initialized and _setup method has been run
    """
    def inner(self, *args):
        if self._wrapped is None:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazySettings(object):
    """Lazy settings module. We want settings to be imported when they are
    accessed not earlier.
    """
    _wrapped = None
    __getattr__ = new_method_proxy(getattr)

    def _setup(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        try:
            settings_module = os.environ['CLOUDCIX_SETTINGS_MODULE']
            if not settings_module:  # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            raise ImportError("You must specify the CLOUDCIX_SETTINGS_MODULE "
                              "environment variable.")
        else:
            settings_module = settings_module.split(":")
            self._wrapped = importlib.import_module(settings_module[0])
            if len(settings_module) > 1:
                self._wrapped = getattr(self._wrapped, settings_module[1])


settings = LazySettings()


def get_required_settings():
    settings_obj = dict()
    try:
        settings_obj['auth_url'] = settings.OPENSTACK_KEYSTONE_URL
        settings_obj['username'] = settings.CLOUDCIX_API_USERNAME
        settings_obj['password'] = settings.CLOUDCIX_API_PASSWORD
        settings_obj['idMember'] = settings.CLOUDCIX_API_ID_MEMBER
    except ImportError:
        settings_obj['auth_url'] = os.environ['OPENSTACK_KEYSTONE_URL']
        settings_obj['username'] = os.environ['CLOUDCIX_API_USERNAME']
        settings_obj['password'] = os.environ['CLOUDCIX_API_PASSWORD']
        settings_obj['idMember'] = os.environ['CLOUDCIX_API_ID_MEMBER']
    return settings_obj


def get_admin_session(**kw):
    settings_obj = get_required_settings()
    t = CloudCIXAuth(
        auth_url=settings_obj['auth_url'],
        username=settings_obj['username'],
        password=settings_obj['password'],
        idMember=settings_obj['idMember'],
        **kw)
    admin_session = KeystoneSession(auth=t)
    admin_session.get_token()
    return admin_session


def get_admin_client():
    settings_obj = get_required_settings()
    admin_session = get_admin_session()
    return KeystoneClient(session=admin_session,
                          auth_url=settings_obj['auth_url'],
                          endpoint_override=settings_obj['auth_url'])
