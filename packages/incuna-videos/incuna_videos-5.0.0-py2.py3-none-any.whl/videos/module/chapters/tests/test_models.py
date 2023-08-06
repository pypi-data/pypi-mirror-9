# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.test import TestCase
from incuna_test_utils.compat import (
    Python2AssertMixin,
    wipe_id_fields_on_django_lt_17,
)
import six

from . import factories
from .. import models


class TestChapter(Python2AssertMixin, TestCase):
    model = models.Chapter

    def test_fields(self):
        expected = wipe_id_fields_on_django_lt_17([
            'id',
            'title',
            'timecode',
            'video',
            'video_id',
            'preview',
        ])
        fields = self.model._meta.get_all_field_names()
        self.assertCountEqual(fields, expected)


class TestChapterUnicode(TestCase):
    def test_cast_to_unicode_string(self):
        expected = 'ツ'
        chapter = factories.ChapterFactory.build(title=expected)
        self.assertEqual(six.text_type(chapter), expected)


class TestChapterSecondsProperty(TestCase):
    def test_seconds(self):
        """16m40s is 1000 seconds"""
        timecode = datetime.time(minute=16, second=40)
        chapter = factories.ChapterFactory.build(timecode=timecode)
        seconds = chapter.seconds
        self.assertEqual(seconds, 1000)
        self.assertIsInstance(seconds, int)
