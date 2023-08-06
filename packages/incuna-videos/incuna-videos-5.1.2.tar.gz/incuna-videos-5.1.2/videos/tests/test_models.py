# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from incuna_test_utils.compat import (
    Python2AssertMixin,
    wipe_id_fields_on_django_lt_17,
)
from six import text_type

from .factories import SourceFactory, VideoFactory
from .. import models


class TestVideo(Python2AssertMixin, TestCase):
    def test_fields(self):
        expected_fields = wipe_id_fields_on_django_lt_17([
            'id',

            'title',
            'slug',
            'preview',
            'length',
            'recorded',
            'created',

            # Extra
            'sub_title',  # Subtitle extension.
            'sources',  # Source model.
            'chapters',  # Chapters extension.
            'speakers',  # Speakers extension.
            'captions_file',  # Captions extension
        ])

        fields = models.Video._meta.get_all_field_names()
        self.assertCountEqual(fields, expected_fields)


class TestVideoManager(TestCase):
    def test_latest(self):
        """The default behaviour of 'Video.objects.latest()'"""
        VideoFactory.create_batch(models.DEFAULT_LATEST_LIMIT + 1)
        latest = models.Video.objects.latest()
        self.assertIs(latest.count(), models.DEFAULT_LATEST_LIMIT)

    def test_latest_none(self):
        """'Latest videos' when no Videos exist"""
        latest = models.Video.objects.latest()
        self.assertFalse(latest.exists())

    def test_latest_2(self):
        """An exact number of 'Video.objects.latest()'"""
        limit = 2
        VideoFactory.create_batch(limit + 1)
        latest = models.Video.objects.latest(limit=limit)
        self.assertIs(latest.count(), limit)

    def test_latest_setting(self):
        """Default setting of 'Video.objects.latest()'"""
        limit = 1
        VideoFactory.create_batch(limit + 1)
        with self.settings(VIDEOS_LATEST_LIMIT=limit):
            latest = models.Video.objects.latest()
        self.assertIs(latest.count(), limit)


class TestVideoUnicode(TestCase):
    def test_cast_to_unicode_string(self):
        expected = 'ツ'
        video = VideoFactory.build(title=expected)
        self.assertEqual(text_type(video), expected)


class TestSource(Python2AssertMixin, TestCase):
    def test_fields(self):
        expected_fields = (
            'id',

            'video',
            'video_id',
            'file',
            'type',
        )

        expected_fields = wipe_id_fields_on_django_lt_17(expected_fields)

        fields = models.Source._meta.get_all_field_names()
        self.assertCountEqual(fields, expected_fields)

    def test_cast_to_unicode_string(self):
        video_title = 'ツ'
        source = SourceFactory.build(
            video__title=video_title,
            type=models.Source.TYPE_MP4,
        )
        expected = '{title} {type}'.format(title=video_title, type='mp4')
        self.assertEqual(text_type(source), expected)

    def test_get_absolute_url(self):
        file_name = 'omgwtf.mp4'
        source = SourceFactory.build(
            type=models.Source.TYPE_MP4,
            file=file_name,
        )
        url = source.get_absolute_url()
        self.assertEqual(url, file_name)
