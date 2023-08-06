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

import reversion
from reversion import get_for_object
from reversion.models import Revision, Version

from tests.models import Person, Pet

# Needs to import admin module to register all models via CompareVersionAdmin/VersionAdmin

from .test_utils.test_cases import BaseTestCase
from .test_utils.test_data import TestData

class PersonPetModelTest(BaseTestCase):
    """
    unittests that used:
        reversion_compare_test_app.models.Person
        reversion_compare_test_app.models.Pet

    Person & Pet are registered with the follow information, so that
    related data would be also stored in django-reversion

    see "Advanced model registration" here:
        https://github.com/etianen/django-reversion/wiki/Low-level-API
    """
    def setUp(self):
        super(PersonPetModelTest, self).setUp()

        test_data = TestData(verbose=False)
#        test_data = TestData(verbose=True)
        self.pet1, self.pet2, self.person = test_data.create_PersonPet_data()

        queryset = get_for_object(self.person)
        self.version_ids = queryset.values_list("pk", flat=True)

    def test_initial_state(self):
        self.assertTrue(reversion.is_registered(Pet))
        self.assertTrue(reversion.is_registered(Person))

        self.assertEqual(Pet.objects.count(), 3)

        self.assertEqual(reversion.get_for_object(self.pet1).count(), 2)
        self.assertEqual(Revision.objects.all().count(), 2)

    def test_select_compare(self):
        response = self.client.get("/admin/tests/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % self.version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % self.version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % self.version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % self.version_ids[1],
        )

    def test_diff(self):
        response = self.client.get(
            "/admin/tests/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":self.version_ids[0], "version_id1":self.version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            """
            <p class="highlight">
                <del>would be changed pet</del> &rarr; <ins>Is changed pet</ins><br />
                <del>- would be deleted pet</del><br />
                <del>- would be removed pet</del><br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 2: change follow related pets.</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "<h3>name</h3>", # person name doesn't changed
            'class="follow"'# All fields are under reversion control
        )

    def test_add_m2m(self):
        with reversion.create_revision():
            new_pet = Pet.objects.create(name="added pet")
            self.person.pets.add(new_pet)
            self.person.save()
            reversion.set_comment("version 3: add a pet")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 12)

        queryset = get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get("/admin/tests/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
        )

        response = self.client.get(
            "/admin/tests/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            """
            <p class="highlight">
                <ins>+ added pet</ins><br />
                Is changed pet<br />
                always the same pet<br />
            </p>
            """,
            "<blockquote>version 3: add a pet</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "<h3>name</h3>", # person name doesn't changed
            'class="follow"'# All fields are under reversion control
        )

    def test_m2m_not_changed(self):
        with reversion.create_revision():
            self.person.name = "David"
            self.person.save()
            reversion.set_comment("version 3: change the name")

        self.assertEqual(Revision.objects.all().count(), 3)
        self.assertEqual(Version.objects.all().count(), 11)

        queryset = get_for_object(self.person)
        version_ids = queryset.values_list("pk", flat=True)
        self.assertEqual(len(version_ids), 3)

        response = self.client.get("/admin/tests/person/%s/history/" % self.person.pk)
#        debug_response(response) # from django-tools
        self.assertContainsHtml(response,
            '<input type="submit" value="compare">',
            '<input type="radio" name="version_id1" value="%i" style="visibility:hidden" />' % version_ids[0],
            '<input type="radio" name="version_id2" value="%i" checked="checked" />' % version_ids[0],
            '<input type="radio" name="version_id1" value="%i" checked="checked" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[1],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
            '<input type="radio" name="version_id2" value="%i" />' % version_ids[2],
        )

        response = self.client.get(
            "/admin/tests/person/%s/history/compare/" % self.person.pk,
            data={"version_id2":version_ids[0], "version_id1":version_ids[1]}
        )
#        debug_response(response) # from django-tools

        self.assertContainsHtml(response,
            '''
            <p><pre class="highlight">
            <del>- Dave</del>
            <ins>+ David</ins>
            </pre></p>
            ''',
            "<blockquote>version 3: change the name</blockquote>", # edit comment
        )
        self.assertNotContainsHtml(response,
            "pet",
            'class="follow"'# All fields are under reversion control
        )


