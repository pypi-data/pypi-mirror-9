from feincms.models import create_base_model

from ..content import VideoContent
from ..models import Video


Video.register_extensions(
    'videos.extensions.captions',
    'videos.extensions.chapters',
    'videos.extensions.speakers',
    'videos.extensions.sub_heading',
)


class DummyPage(create_base_model()):
    """A fake class for holding content"""


DummyPage.register_regions(('main', 'Main content area'))
DummyPage.create_content_type(VideoContent, TYPE_CHOICES=(
    ('block', 'Block'),
))
