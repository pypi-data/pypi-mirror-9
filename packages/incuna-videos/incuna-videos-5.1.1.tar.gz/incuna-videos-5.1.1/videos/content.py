from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class VideoContent(models.Model):
    """Display a video in all its glorious formats"""
    video = models.ForeignKey(
        'videos.Video',
        verbose_name=_('video'),
        # Reverse related name is unused, and causes clashes, so it's gone.
        related_name='+',
    )

    class Meta:
        abstract = True
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    @classmethod
    def initialize_type(cls, TYPE_CHOICES=None):
        if TYPE_CHOICES is None:
            msg = 'You have to set TYPE_CHOICES when creating a {}'
            raise ImproperlyConfigured(msg.format(cls.__name__))

        cls.add_to_class(
            'type',
            models.CharField(
                _('type'),
                max_length=255,
                choices=TYPE_CHOICES,
                default=TYPE_CHOICES[0][0],
            )
        )

    def get_template_names(self):
        return [
            'videos/content/%s_%s.html' % (self.region, self.type),
            'videos/content/%s.html' % self.region,
            'videos/content/%s.html' % self.type,
            'videos/content/default.html',
        ]

    def get_context_data(self, **context):
        context.update({
            'video': self.video,
            'type': self.type,
            'sources': self.video.sources.all(),
        })
        extensions = ('chapters', 'speakers')
        for extension in extensions:
            manager = getattr(self.video, extension, None)
            if manager:
                context.update({extension: manager.all()})
        return context

    def render(self, **kwargs):
        return render_to_string(
            self.get_template_names(),
            self.get_context_data(**kwargs),
            context_instance=kwargs.get('context'),
        )


class JsonVideoContent(VideoContent):
    class Meta(VideoContent.Meta):
        abstract = True

    def json(self, **kwargs):
        """Return a json serializable representation of the video."""
        video = self.video

        def source_json(source):
            """Return a json serializable representation of a video source."""
            return {
                'file': source.file.url,
                'type': source.type,
            }

        return {
            'created': video.created,
            'length': video.length,
            'preview': video.preview.url,
            'recorded': video.recorded,
            'slug': video.slug,
            'sources': [source_json(source) for source in video.sources.all()],
            'title': video.title,
        }
