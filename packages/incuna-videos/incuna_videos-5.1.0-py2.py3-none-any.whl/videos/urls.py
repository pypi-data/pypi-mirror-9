from django.conf.urls import url

from .views import VideoDetail, VideoList, VideoListLatest


urlpatterns = [
    url(r'^$', VideoListLatest.as_view(), name='videos_latest'),
    url(r'^all/$', VideoList.as_view(), name='videos_all'),
    url(r'^(?P<slug>[a-z0-9_-]+).html$', VideoDetail.as_view(), name='videos_detail'),
]
