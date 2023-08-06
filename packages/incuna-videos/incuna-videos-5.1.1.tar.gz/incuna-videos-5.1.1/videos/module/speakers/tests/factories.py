import factory

from .. import models


class SpeakerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Speaker

    name = factory.Sequence('Speaker {}'.format)
    slug = factory.Sequence('speaker-{}'.format)
