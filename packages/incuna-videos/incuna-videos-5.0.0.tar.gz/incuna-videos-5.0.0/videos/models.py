from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from feincms.extensions import ExtensionsMixin


DEFAULT_LATEST_LIMIT = 3


class VideoManager(models.Manager):
    def latest(self, limit=None):
        if limit is None:
            limit = getattr(settings, 'VIDEOS_LATEST_LIMIT', DEFAULT_LATEST_LIMIT)
        return self.get_query_set()[:limit]


@python_2_unicode_compatible
class Video(models.Model, ExtensionsMixin):
    """
    Extensible video model.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=127,
        editable=True,
        unique=True,
        help_text=(
            "This will be automatically generated from the title, and " +
            "is used as the video's website address"
        ),
    )
    preview = models.FileField(max_length=255, upload_to='videos/preview', null=True, blank=True, help_text=_('Preview image for this video.'))
    length = models.TimeField(blank=True, null=True, help_text='hh:mm:ss')
    recorded = models.DateField(blank=True, null=True)
    created = models.DateTimeField(editable=False, default=datetime.datetime.now)

    objects = VideoManager()

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title

    @property
    def length_display(self):
        raise NotImplementedError('https://github.com/incuna/incuna-videos/issues/8')
        return timesince(datetime.time(0, 0, 0), self.length)

    @classmethod
    def register_extension(cls, register_fn):
        from .admin import VideoAdmin
        register_fn(cls, VideoAdmin)


@python_2_unicode_compatible
class Source(models.Model):
    """
    Video source (inspired by the HTML5 <source> tag)
    """
    TYPE_MP4 = 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"'
    TYPE_WEBM = 'video/webm; codecs="vp8, vorbis"'
    TYPE_OGG = 'video/ogg; codecs="theora, vorbis"'
    TYPE_CHOICES = getattr(settings, 'VIDEO_TYPE_CHOICES', (
        (TYPE_MP4, 'mp4'),
        (TYPE_WEBM, 'webm'),
        (TYPE_OGG, 'ogg'),
    ))
    video = models.ForeignKey(Video, related_name='sources')
    file = models.FileField(upload_to='videos/%Y/%m/')
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)

    def __str__(self):
        return '{video_title} {type}'.format(
            video_title=self.video.title,
            type=self.get_type_display(),
        )

    def get_absolute_url(self):
        return self.file.url
