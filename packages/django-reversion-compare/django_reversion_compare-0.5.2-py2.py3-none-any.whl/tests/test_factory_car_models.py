#!/usr/bin/env python
# coding: utf-8

"""
    django-reversion-compare unittests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    I used the setup from reversion_compare_test_project !

    TODO:
        * models.OneToOneField()
        * models.IntegerField()

    :copyleft: 2012-2015 by the django-reversion-compare team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import datetime

from django.core.urlresolvers import reverse
from django.db.models.loading import get_models, get_app
from django.test import TestCase
from django.contrib.auth.models import User

#
try:
    import django_tools
except ImportError as err:
    msg = (
        "Please install django-tools for unittests"
        " - https://github.com/jedie/django-tools/"
        " - Original error: %s"
    ) % err
    raise ImportError(msg)
from django_tools.unittest_utils.BrowserDebug import debug_response

import reversion
from reversion import get_for_object
from reversion.models import Revision, Version

from reversion_compare import helpers

from .models import Factory, Car
from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData

class FactoryCarModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Factory
        reversion_compare_test_app.models.Car

    Factory & Car would be registered only in admin.py
    so no relation data would be stored
    """
    def setUp(self):
        super(FactoryCarModelTest, self).setUp()

        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.car = test_data.create_FactoryCar_data()

        queryset = get_for_object(self.car)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(Factory))
        self.assertTrue(reversion.is_registered(Car))

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(len(self.version_ids), 3)
        self.assertEqual(Version.objects.all().count(), 10)

    def test_select_compare(self):
        response = self.client.get("/admin/tests/car/%s/history/" % self.car.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[2],
        )

    def test_diff1(self):
        response = self.client.get(
            "/admin/tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2":self.version_ids[1], "version_id1":self.version_ids[2]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">
                <del>- would be deleted supplier</del><br />
                <del>- would be removed supplier</del><br />
                <ins>+ new, would be renamed supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>', # info for non-follow related informations
            '<blockquote>version 2: change ForeignKey and ManyToManyField.</blockquote>', # edit comment
        )

    def test_diff2(self):
        response = self.client.get(
            "/admin/tests/car/%s/history/compare/" % self.car.pk,
            data={"version_id2":self.version_ids[0], "version_id1":self.version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            "<del>- motor-car one</del>",
            "<ins>+ motor-car II</ins>",

            '<h3>manufacturer<sup class="follow">*</sup></h3>',
            '<h3>supplier<sup class="follow">*</sup></h3>',
            '''
            <p class="highlight">
                <del>new, would be renamed supplier</del> &rarr; <ins>not new anymore supplier</ins><br />
                always the same supplier<sup class="follow">*</sup><br />
            </p>
            ''',
            '<h4 class="follow">Note:</h4>', # info for non-follow related informations
            '<blockquote>version 3: change CharField, ForeignKey and ManyToManyField.</blockquote>', # edit comment
        )
