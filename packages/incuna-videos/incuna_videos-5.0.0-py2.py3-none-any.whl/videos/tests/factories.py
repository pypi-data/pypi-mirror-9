import factory

from .. import models


class SourceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Source

    file = 'randomfile.mp4'
    type = models.Source.TYPE_MP4  # An arbitrary default for the factory
    video = factory.SubFactory('videos.tests.factories.VideoFactory')


class VideoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Video

    title = factory.Sequence('Video {}'.format)
    slug = factory.Sequence('video-{}'.format)
    captions_file = 'captionfile.txt'
