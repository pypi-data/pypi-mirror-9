from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestVideoURLs(URLTestCase):
    def test_latest_url(self):
        self.assert_url_matches_view(
            view=views.VideoListLatest,
            expected_url='/videos/',
            url_name='videos_latest',
        )

    def test_all_url(self):
        self.assert_url_matches_view(
            view=views.VideoList,
            expected_url='/videos/all/',
            url_name='videos_all',
        )

    def test_detail_url(self):
        slug = 'video-slug'
        self.assert_url_matches_view(
            view=views.VideoDetail,
            expected_url='/videos/{slug}.html'.format(slug=slug),
            url_name='videos_detail',
            url_kwargs={'slug': slug},
        )
