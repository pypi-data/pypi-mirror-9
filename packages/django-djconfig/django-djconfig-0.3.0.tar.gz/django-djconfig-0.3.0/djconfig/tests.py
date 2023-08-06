# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.test.utils import override_settings
from django.core.cache import cache as _cache
from django import forms
from django.core.cache import get_cache
from django.conf import settings

from . import registry
from . import forms as djconfig_forms
from . import settings as djconfig_settings
from .utils import prefixer
from .utils import override_djconfig
from .conf import Config, config
from .forms import ConfigForm
from .models import Config as ConfigModel
from .middleware import DjConfigLocMemMiddleware


class FooForm(ConfigForm):

    boolean = forms.BooleanField(initial=True, required=False)
    boolean_false = forms.BooleanField(initial=False, required=False)
    char = forms.CharField(initial="foo")
    email = forms.EmailField(initial="foo@bar.com")
    float_number = forms.FloatField(initial=1.23)
    integer = forms.IntegerField(initial=123)
    url = forms.URLField(initial="foo.com/")


class DjConfigTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()
        registry._registered_forms.clear()

        self.cache = get_cache(djconfig_settings.BACKEND)

    def test_register(self):
        """
        register forms
        """
        registry.register(FooForm)
        self.assertSetEqual(registry._registered_forms, {FooForm, })

    def test_register_invalid_form(self):
        """
        register invalid forms
        """
        class BadForm(forms.Form):
            """"""

        self.assertRaises(AssertionError, registry.register, BadForm)


class BarForm(ConfigForm):

    char = forms.CharField(initial="foo")


class DjConfigFormsTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()
        registry._registered_forms.clear()

    def test_config_form_populate_if_loaded(self):
        """
        config form, populate initial data only if the config is loaded
        """
        registry.register(BarForm)
        config._set("char", "foo2")

        form = BarForm()
        self.assertTrue('char' not in form.initial)

        config._is_loaded = True
        form = BarForm()
        self.assertEqual(form.initial['char'], 'foo2')

    def test_config_form_allow_initial_overwrite(self):
        """
        config form, allow user to pass initial data
        """
        registry.register(BarForm)
        config._set("char", "foo2")
        config._is_loaded = True

        form = BarForm(initial={'char': 'bar', })
        self.assertEqual(form.initial['char'], 'bar')

    def test_config_form(self):
        """
        config form
        """
        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()
        config = ConfigModel.objects.get(key="char")
        self.assertEqual(config.value, "foo2")

    def test_config_form_update(self):
        """
        config form
        """
        ConfigModel.objects.create(key="char", value="bar")

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()
        config = ConfigModel.objects.get(key="char")
        self.assertEqual(config.value, "foo2")

    def test_config_form_cache_update(self):
        """
        config form, update cache on form save
        """
        registry.register(BarForm)

        form = BarForm(data={"char": "foo2", })
        self.assertTrue(form.is_valid())
        form.save()

        cache = get_cache(djconfig_settings.BACKEND)
        self.assertEqual(cache.get(prefixer('char')), "foo2")

    def test_config_form_updated_at(self):
        """
        updated_at should get update on every save() call
        """
        now = djconfig_forms.timezone.now()

        class TZMock:
            @classmethod
            def now(self):
                return now

        orig_djconfig_forms_timezone, djconfig_forms.timezone = djconfig_forms.timezone, TZMock
        try:
            form = BarForm(data={"char": "foo2", })
            self.assertTrue(form.is_valid())
            form.save()
            updated_at_a = ConfigModel.objects.get(key="_updated_at").value

            now += datetime.timedelta(seconds=1)

            form = BarForm(data={"char": "foo2", })
            self.assertTrue(form.is_valid())
            form.save()
            updated_at_b = ConfigModel.objects.get(key="_updated_at").value

            self.assertNotEqual(updated_at_a, updated_at_b)
        finally:
            djconfig_forms.timezone = orig_djconfig_forms_timezone


class DjConfigConfTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()
        registry._registered_forms.clear()
        self.cache = get_cache(djconfig_settings.BACKEND)

    def test_config_attr_error(self):
        """
        config attribute error when it's not in keys
        """
        config = Config()

        def wrapper():
            return config.foo

        self.assertRaises(AttributeError, wrapper)

        config._set('foo', 'bar')
        self.assertEqual(wrapper(), 'bar')

    def test_config_set(self):
        """
        config set adds the item
        """
        config = Config()
        config._set('foo', 'bar')
        self.assertTrue('foo' in config._keys)
        self.assertEqual(config.foo, 'bar')

    def test_config_set_many(self):
        """
        config set adds the key
        """
        config = Config()
        config._set_many({'foo': 'bar', })
        self.assertTrue('foo' in config._keys)
        self.assertEqual(config.foo, 'bar')

    def test_config_load(self):
        """
        Load initial configuration into the cache
        """
        registry.register(FooForm)
        config._lazy_load()
        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = self.cache.get_many([prefixer(k) for k in keys])
        self.assertDictEqual(values, {prefixer('boolean'): True,
                                      prefixer('boolean_false'): False,
                                      prefixer('char'): "foo",
                                      prefixer('email'): "foo@bar.com",
                                      prefixer('float_number'): 1.23,
                                      prefixer('integer'): 123,
                                      prefixer('url'): "foo.com/"})

    def test_config_load_from_database(self):
        """
        Load configuration into the cache
        """
        data = [ConfigModel(key='boolean', value=False),
                ConfigModel(key='boolean_false', value=True),
                ConfigModel(key='float_number', value=2.1),
                ConfigModel(key='char', value="foo2"),
                ConfigModel(key='email', value="foo2@bar.com"),
                ConfigModel(key='integer', value=321),
                ConfigModel(key='url', value="foo2.com/")]
        ConfigModel.objects.bulk_create(data)

        registry.register(FooForm)
        config._lazy_load()

        keys = ['boolean', 'boolean_false', 'char', 'email', 'float_number', 'integer', 'url']
        values = self.cache.get_many([prefixer(k) for k in keys])
        self.assertDictEqual(values, {prefixer('boolean'): False,
                                      prefixer('boolean_false'): True,
                                      prefixer('float_number'): 2.1,
                                      prefixer('char'): "foo2",
                                      prefixer('email'): "foo2@bar.com",
                                      prefixer('integer'): 321,
                                      prefixer('url'): "http://foo2.com/"})

        # use initial if the field is not found in the db
        ConfigModel.objects.get(key='char').delete()
        config._reset()
        config._lazy_load()
        self.assertEqual(self.cache.get(prefixer('char')), "foo")

    def test_config_load_unicode(self):
        """
        Load configuration into the cache
        """
        ConfigModel.objects.create(key='char', value=u"áéíóú")
        registry.register(FooForm)
        config._lazy_load()
        self.assertEqual(self.cache.get(prefixer('char')), u"áéíóú")

    def test_config_load_from_database_invalid(self):
        """
        Load initial if the db value is invalid
        """
        ConfigModel.objects.create(key='integer', value="string")
        registry.register(FooForm)
        config._lazy_load()
        self.assertEqual(self.cache.get(prefixer('integer')), 123)

    def test_config_load_updated_at(self):
        """
        Load updated_at
        """
        registry.register(FooForm)
        config._lazy_load()
        value = self.cache.get(prefixer("_updated_at"))
        self.assertIsNone(value)

        ConfigModel.objects.create(key="_updated_at", value="string")
        config._reset()
        config._lazy_load()
        value = self.cache.get(prefixer("_updated_at"))
        self.assertEqual(value, "string")

    def test_config_lazy_load(self):
        """
        Load the config the first time you access an attribute
        """
        registry.register(FooForm)
        # registry.load()
        value = self.cache.get(prefixer("char"))
        self.assertIsNone(value)

        self.assertEqual(config.char, "foo")

    def test_config_lazy_load_race_condition(self):
        """
        It sets is_loaded *after* the reload.
        """
        class ConfigMock(Config):
            def _reload(self):
                raise ValueError

        config = ConfigMock()
        self.assertFalse(config._is_loaded)
        self.assertRaises(ValueError, config._lazy_load)
        self.assertFalse(config._is_loaded)

    def test_config_lazy_load_once(self):
        """
        Reload is not called if already loaded
        """
        class ConfigMock(Config):
            def _reload(self):
                raise ValueError

        config = ConfigMock()
        config._is_loaded = True
        self.assertIsNone(config._lazy_load())

    def test_config_lazy_load_ok(self):
        """
        It sets is_loaded *after* the reload.
        """
        config = Config()

        self.assertFalse(config._is_loaded)
        config._lazy_load()
        self.assertTrue(config._is_loaded)

    def test_config_reload_in_keys(self):
        """
        Load the config the first time you access an attribute
        """
        registry.register(FooForm)
        config._reload()
        self.assertTrue('char' in config._keys)
        self.assertEqual(config.char, "foo")

    def test_config_reset(self):
        """
        Reset turn is_loaded to False
        """
        config._is_loaded = True
        config._reset()
        self.assertFalse(config._is_loaded)


TEST_CACHES = {
    'good': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'bad': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


class DjConfigMiddlewareTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()
        registry._registered_forms.clear()

    def test_config_middleware_process_request(self):
        """
        config middleware, reload cache
        """
        ConfigModel.objects.create(key="char", value="foo")
        registry.register(BarForm)
        config._lazy_load()
        cache = get_cache(djconfig_settings.BACKEND)

        cache.set(prefixer('char'), None)
        self.assertIsNone(cache.get(prefixer('char')))

        # Should not reload since _updated_at does not exists (form was not saved)
        middleware = DjConfigLocMemMiddleware()
        middleware.process_request(request=None)
        self.assertIsNone(cache.get(prefixer('char')))

        # Changing _updated_at should make it reload
        ConfigModel.objects.create(key="_updated_at", value="111")
        middleware.process_request(request=None)
        self.assertEqual(cache.get(prefixer('char')), "foo")
        self.assertEqual(cache.get(prefixer("_updated_at")), "111")

        # It does not update again, since _updated_at has not changed
        ConfigModel.objects.filter(key="char").update(value="bar")
        middleware.process_request(request=None)
        self.assertNotEqual(cache.get(prefixer('char')), "bar")
        self.assertEqual(cache.get(prefixer("_updated_at")), "111")

        # Changing _updated_at should make it reload
        ConfigModel.objects.filter(key="_updated_at").update(value="222")
        middleware.process_request(request=None)
        self.assertEqual(cache.get(prefixer('char')), "bar")
        self.assertEqual(cache.get(prefixer("_updated_at")), "222")

    def test_config_middleware_check_backend(self):
        """
        only LocMemCache should be allowed
        """
        org_cache, org_djbackend = settings.CACHES, djconfig_settings.BACKEND
        try:
            settings.CACHES = TEST_CACHES

            djconfig_settings.BACKEND = 'good'
            middleware = DjConfigLocMemMiddleware()
            self.assertIsNone(middleware.check_backend())

            djconfig_settings.BACKEND = 'bad'
            self.assertRaises(ValueError, middleware.check_backend)
        finally:
            settings.CACHES, djconfig_settings.BACKEND = org_cache, org_djbackend


TESTING_BACKEND_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'djconfig': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-djconfig',
    }
}


class DjConfigBackendTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()

    @override_settings(CACHES=TESTING_BACKEND_CACHES)
    def test_config_testing_backend(self):
        """
        TestingCache can't be cleared (it is persistent)
        """
        cache = get_cache('djconfig')
        default_cache = get_cache('default')

        cache.set('foo', "foovalue")
        self.assertIsNotNone(cache.get('foo'))

        default_cache.set('bar', "barvalue")
        self.assertIsNotNone(default_cache.get('bar'))

        _cache.clear()
        self.assertIsNotNone(cache.get('foo'))
        self.assertIsNone(default_cache.get('foo'))


class DjConfigUtilsTest(TestCase):

    def setUp(self):
        _cache.clear()
        config._reset()
        registry._registered_forms.clear()

    def test_override_djconfig(self):
        """
        Sets config variables temporarily
        """
        @override_djconfig(foo='bar', foo2='bar2')
        def my_test(my_var):
            return my_var, config.foo, config.foo2

        config._set('foo', 'org')
        config._set('foo2', 'org2')

        res = my_test("stuff")
        self.assertEqual(res, ("stuff", 'bar', 'bar2'))
        self.assertEqual((config.foo, config.foo2), ("org", 'org2'))

    def test_override_djconfig_except(self):
        """
        Sets config variables temporarily, even on exceptions
        """
        @override_djconfig(foo='bar')
        def my_test():
            raise AssertionError

        config._set('foo', 'org')

        try:
            my_test()
        except AssertionError:
            pass

        self.assertEqual(config.foo, "org")
