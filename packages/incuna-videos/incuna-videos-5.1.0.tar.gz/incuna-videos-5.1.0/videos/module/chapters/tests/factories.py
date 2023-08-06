import datetime

import factory

from .. import models
from videos.tests.factories import VideoFactory


class ChapterFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Chapter
    video = factory.SubFactory(VideoFactory)
    title = factory.Sequence('Video {}'.format)
    timecode = datetime.time(minute=5)
