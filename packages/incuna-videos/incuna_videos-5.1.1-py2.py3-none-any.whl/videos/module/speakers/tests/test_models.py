# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from incuna_test_utils.compat import (
    Python2AssertMixin,
    wipe_id_fields_on_django_lt_17,
)
from six import text_type

from . import factories
from .. import models


class TestSpeaker(Python2AssertMixin, TestCase):
    def test_fields(self):
        expected = wipe_id_fields_on_django_lt_17([
            'id',
            'name',
            'slug',
            'video',  # Incoming M2M
        ])
        fields = models.Speaker._meta.get_all_field_names()
        self.assertCountEqual(fields, expected)

    def test_cast_to_unicode_string(self):
        expected = 'ツ'
        speaker = factories.SpeakerFactory.build(name=expected)
        self.assertEqual(text_type(speaker), expected)
