# -*- coding: utf-8 -*-
from rest_framework_extensions.test import APITestCase

from .models import KeyConstructorUserProperty, KeyConstructorUserModel


class ListSqlQueryKeyBitTestBehaviour__with_bad_filter_arguments(APITestCase):
    """Regression tests for https://github.com/chibisov/drf-extensions/issues/28#issuecomment-51711927

    `rest_framework.filters.DjangoFilterBackend` uses defalut `FilterSet`.
    When there is no filtered fk in db, then `FilterSet.form` is invalid with errors:
        {'property': [u'Select a valid choice. That choice is not one of the available choices.']}
    In that case `FilterSet.qs` returns `self.queryset.none()`
    """
    urls = 'tests_app.tests.functional.key_constructor.bits.urls'

    def test_with_fk_in_db(self):
        KeyConstructorUserProperty.objects.create(name='some property')

        # list
        response = self.client.get('/users/?property=1')
        self.assertEqual(response.status_code, 200)

        # retrieve
        response = self.client.get('/users/1/?property=1')
        self.assertEqual(response.status_code, 404)

    def test_without_fk_in_db(self):
        # list
        response = self.client.get('/users/?property=1')
        self.assertEqual(response.status_code, 200)

        # retrieve
        response = self.client.get('/users/1/?property=1')
        self.assertEqual(response.status_code, 404)