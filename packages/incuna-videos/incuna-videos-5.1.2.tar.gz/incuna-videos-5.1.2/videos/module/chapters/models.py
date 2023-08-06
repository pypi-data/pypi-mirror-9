import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Chapter(models.Model):
    """Video section"""
    video = models.ForeignKey('videos.Video', related_name='chapters')
    title = models.CharField(max_length=255)
    timecode = models.TimeField(help_text='hh:mm:ss')
    preview = models.ImageField(upload_to='videos/chapter/', null=True, blank=True, help_text=_('Preview image for this chapter.'))

    class Meta:
        app_label = 'videos'
        ordering = ('timecode',)

    def __str__(self):
        return self.title

    @property
    def seconds(self):
        timecode = self.timecode
        seconds = datetime.timedelta(
            hours=timecode.hour,
            minutes=timecode.minute,
            seconds=timecode.second,
        ).total_seconds()
        return int(seconds)
