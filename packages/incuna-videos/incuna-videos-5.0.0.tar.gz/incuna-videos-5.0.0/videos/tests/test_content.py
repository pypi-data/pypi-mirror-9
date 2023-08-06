from django.test import TestCase
from incuna_test_utils.compat import Python2AssertMixin

from . import factories
from .models import DummyPage
from ..content import VideoContent
from videos.module.chapters.tests.factories import ChapterFactory
from videos.module.speakers.tests.factories import SpeakerFactory


class VideoContentTest(Python2AssertMixin, TestCase):
    model = DummyPage.content_type_for(VideoContent)

    def test_get_context_data(self):
        content = self.model(region='main')
        video = factories.VideoFactory.create()
        source = factories.SourceFactory.create(video=video)
        chapter = ChapterFactory.create(video=video)
        speaker = SpeakerFactory.create()
        video.speakers.add(speaker)
        content.video = video
        request = 'dummy'
        context = content.get_context_data(request=request)

        expected = {
            'type': 'block',  # Default set in 'models.py' when registered
            'video': content.video,
            'request': request,
            'sources': [source],

            # Extras included by standard extensions
            'chapters': [chapter],
            'speakers': [speaker],
        }
        self.assertCountEqual(context, expected)

    def test_get_template_names(self):
        content = self.model(region='main')
        expected = [
            'videos/content/main_block.html',  # Region && type
            'videos/content/main.html',  # Region default
            'videos/content/block.html',  # Just type
            'videos/content/default.html',  # Default/Last resort
        ]
        self.assertCountEqual(content.get_template_names(), expected)

    def test_render(self):
        content = self.model(region='main')
        source = factories.SourceFactory.create()
        content.video = source.video
        with self.assertNumQueries(3):
            # Three queries:
            # - Get Speakers
            # - Get Sources
            # - Get Chapters
            result = content.render()

        # Is there a link to the Source?
        source_str = '<source src="{}"'.format(source.get_absolute_url())
        self.assertIn(source_str, result)

        # Is there a link to the captions_file (subtitles)?
        captions_str = '<track src="{}"'.format(source.video.captions_file.url)
        self.assertIn(captions_str, result)

        # Is there a <video> tag?
        video_str = '<video'
        self.assertIn(video_str, result)
        end_video_str = '</video>'
        self.assertIn(end_video_str, result)

        # Is the Source within the <video> tag?
        self.assertLess(result.index(video_str), result.index(source_str))
        self.assertLess(result.index(source_str), result.index(end_video_str))

        # Is the Caption within the <video> tag?
        self.assertLess(result.index(video_str), result.index(captions_str))
        self.assertLess(result.index(captions_str), result.index(end_video_str))


class TestContentAccessible(TestCase):
    def test_object_has_content(self):
        concrete_content_type = DummyPage.content_type_for(VideoContent)
        content = concrete_content_type.objects.create(
            region='main',
            parent=DummyPage.objects.create(),
            video=factories.VideoFactory.create(),
        )

        page = DummyPage.objects.get()
        self.assertSequenceEqual(page.content.main, [content])
