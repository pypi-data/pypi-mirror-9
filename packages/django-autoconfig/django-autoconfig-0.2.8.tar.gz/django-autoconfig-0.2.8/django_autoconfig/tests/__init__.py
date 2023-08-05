'''Tests for django-autoconfig.'''
# pylint: disable=C0103
# pylint: disable=R0904

from django_autoconfig import autoconfig

import copy
from django.core.exceptions import ImproperlyConfigured
import django.core.urlresolvers
from django.core.urlresolvers import resolve
from django import test
from django.utils import unittest

class ConfigureSettingsTestCase(test.TestCase):
    '''Test the configure_settings method.'''

    BASE_SETTINGS = {
        'LIST_SETTING': [1, 2],
        'BOOLEAN_SETTING': True,
        'DICT_SETTING': {
            'key1': 'value1',
        },
    }

    def setUp(self):
        self.settings_dict = copy.deepcopy(self.BASE_SETTINGS)

    def test_list_merging(self):
        '''
        Test that list settings are merged correctly
        '''

        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_list']
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['LIST_SETTING'], [1, 2, 3])

    def test_new_setting(self):
        '''
        A new setting (i.e. not in the DJANGO_SETTINGS_MODULE)
        should just end up as the new value.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_new_setting']
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['NEW_LIST_SETTING'], [1, 2, 3])

    def test_list_setting_from_defaults(self):
        '''
        A list setting that exists in the django.conf.settings.global_settings
        should merge with the default, not replace it entirely.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_middleware']
        autoconfig.configure_settings(self.settings_dict)
        self.assertIn('my.middleware', self.settings_dict['MIDDLEWARE_CLASSES'])
        self.assertIn('django.middleware.common.CommonMiddleware', self.settings_dict['MIDDLEWARE_CLASSES'])

    def test_no_autoconfig(self):
        '''
        An app with no autoconfig shouldn't break things.
        '''
        self.settings_dict['INSTALLED_APPS'] = [
            'django_autoconfig.tests.app_no_autoconfig',
            'django',
        ]
        autoconfig.configure_settings(self.settings_dict)

    def test_blank_autoconfig(self):
        '''
        An app with a blank autoconfig shouldn't break things.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_blank_autoconfig']
        autoconfig.configure_settings(self.settings_dict)

    def test_booleans(self):
        '''
        Things we can't merge just get replaced.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_boolean']
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['DEBUG'], True)

    def test_inconsistency(self):
        '''
        Check for required inconsistencies.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_boolean', 'django_autoconfig.tests.app_boolean_inconsistent']
        with self.assertRaises(ImproperlyConfigured):
            autoconfig.configure_settings(self.settings_dict)

    def test_relationship(self):
        '''
        Test putting things somewhere other than at the end of the list.
        '''
        self.settings_dict['INSTALLED_APPS'] = [
            'django_autoconfig.tests.app1',
            'django_autoconfig.tests.app2',
            'django_autoconfig.tests.app_relationship',
        ]
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(
            self.settings_dict['INSTALLED_APPS'],
            [
                'django_autoconfig.tests.app_relationship',
                'django_autoconfig.tests.app1',
                'django_autoconfig.tests.app3',
                'django_autoconfig.tests.app2',
            ],
        )

    def test_default_setting(self):
        '''
        A setting in the DEFAULTS section should be used like merging.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_default_settings']
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['DEFAULT_SETTING'], [1, 2, 3])

    def test_default_existing_setting(self):
        '''
        A setting in the DEFAULTS section should only be used if
        it doesn't already exist.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_default_settings']
        self.settings_dict['DEFAULT_SETTING'] = [4, 5, 6]
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['DEFAULT_SETTING'], [4, 5, 6])

    def test_importerror_from_no_parent(self):
        '''
        An import error due to the parent module not existing should be raised.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['i.do.not.exist']
        with self.assertRaises(ImportError):
            autoconfig.configure_settings(self.settings_dict)

    def test_importerror_from_import_error(self):
        '''
        An import error due to the module itself generating an import error should be raised.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_broken_autoconfig']
        with self.assertRaises(ImportError) as exception_manager:
            autoconfig.configure_settings(self.settings_dict)
        self.assertIn('flibble', str(exception_manager.exception))

    def test_disabled_autoconfig(self):
        '''
        Test the ability to disable autoconfig for some apps.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django_autoconfig.tests.app_list']
        self.settings_dict['AUTOCONFIG_DISABLED_APPS'] = ['django_autoconfig.tests.app_list']
        autoconfig.configure_settings(self.settings_dict)
        self.assertEqual(self.settings_dict['LIST_SETTING'], [1, 2])

    def test_contrib_autoconfig(self):
        '''
        Test autoconfig provided by us instead of the app.
        '''
        self.settings_dict['INSTALLED_APPS'] = ['django.contrib.auth']
        autoconfig.configure_settings(self.settings_dict)
        self.assertIn('django.contrib.sessions', self.settings_dict['INSTALLED_APPS'])

    def test_logging_premature_imports(self):
        '''
        Test that logging doesn't cause premature imports.
        '''

        import logging
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        output = StringIO()
        stream_handler = logging.StreamHandler(output)
        logger = logging.getLogger('django_autoconfig.autoconfig')
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)

        self.triggered = False
        class Trap(object):
            def __init__(self, sentinel):
                self.sentinel = sentinel
            def __str__(self):
                self.sentinel.triggered = True
                return 'triggered!'

        autoconfig.merge_dictionaries({}, {'LOGIN_URL': Trap(self)})
        self.assertFalse(self.triggered)

        logger.removeHandler(stream_handler)

    def test_premature_evaluation(self):
        '''
        Make sure using lazily reversed urls doesn't cause evaluation
        of the url prior to finishing the settings.
        '''
        self.triggered = False
        autoconfig.merge_dictionaries({'LOGIN_URL': '/login/'}, {'LOGIN_URL': django.core.urlresolvers.reverse_lazy('does.not.exist')})
        self.assertFalse(self.triggered)


class ConfigureUrlsTestCase(test.TestCase):
    '''Test the autoconfiguration of the urlconf.'''
    urls = 'django_autoconfig.autourlconf'

    def create_urlconf(self, apps, **kwargs):
        '''Create a urlconf from a list of apps.'''
        self.urlpatterns = autoconfig.configure_urls(apps, **kwargs)
        django.core.urlresolvers._resolver_cache = {}

    def test_urls(self):
        '''Test a simple url autoconfiguration.'''
        self.create_urlconf(['django_autoconfig.tests.app_urls'])
        resolve('/django-autoconfig.tests.app-urls/index/', urlconf=self)

    def test_blank_urls(self):
        '''Test a url autoconfiguration with an app with a blank urls.py.'''
        self.create_urlconf(['django_autoconfig.tests.app_urls', 'django_autoconfig.tests.app_blank_urls'])
        with self.assertRaises(django.core.urlresolvers.Resolver404):
            resolve('/django-autoconfig.tests.app-blank-urls/index/', urlconf=self)

    def test_missing_app_urls(self):
        '''Test a url autoconfiguration with an app without urls.'''
        self.create_urlconf(['django_autoconfig.tests.app_urls', 'django_autoconfig.tests.app1'])
        with self.assertRaises(django.core.urlresolvers.Resolver404):
            resolve('/django-autoconfig.tests.app1/index/', urlconf=self)

    def test_broken_urls(self):
        '''Test a url autoconfiguration with a urlconf that fails due to a missing import.'''
        with self.assertRaises(ImportError):
            self.create_urlconf(['django_autoconfig.tests.app_broken_urls'])

    def test_no_index_view(self):
        '''Test the index view functionality, if it's not used.'''
        self.create_urlconf(['django_autoconfig.tests.app_urls'])
        with self.assertRaises(django.core.urlresolvers.Resolver404):
            resolve('/', urlconf=self).func

    @unittest.skipIf(django.VERSION < (1, 6), 'AUTOCONFIG_INDEX_VIEW needs Django >= 1.6')
    def test_broken_index_view(self):
        '''Test the index view functionality with a broken view.'''
        self.create_urlconf([], index_view='does-not-exist')
        view = resolve('/', urlconf=self).func
        response = view(test.RequestFactory().get(path='/'))
        self.assertEqual(response.status_code, 410)

class IndexViewTestCase(test.TestCase):
    '''Test the index view.'''
    urls = 'django_autoconfig.tests.index_view_urlconf'

    @unittest.skipIf(django.VERSION < (1, 6), 'AUTOCONFIG_INDEX_VIEW needs Django >= 1.6')
    def test_index_view(self):
        '''Test the index view functionality.'''
        response = self.client.get('/')
        #view = resolve('/').func
        #response = view(test.RequestFactory().get(path='/'))
        #resolve('/django-autoconfig.tests.app-urls/index/', urlconf=self)
        self.assertEqual(response.status_code, 301)
        response = self.client.get('/', follow=True)
        self.assertContains(response, 'django_autoconfig/tests/app_urls/index view', status_code=200)
