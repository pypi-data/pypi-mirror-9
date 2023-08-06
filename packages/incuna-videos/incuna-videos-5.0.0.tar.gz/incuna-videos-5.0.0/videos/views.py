from django.views.generic import DetailView, ListView

from .models import Video


class VideoList(ListView):
    template_name = 'videos/list.html'
    model = Video


class VideoListLatest(VideoList):
    def get_queryset(self):
        return Video.objects.latest()


class VideoDetail(DetailView):
    template_name = 'videos/detail.html'
    model = Video

    def get_context_data(self, **kwargs):
        extensions = ('chapters', 'speakers')
        for extension in extensions:
            manager = getattr(self.object, extension, None)
            if manager:
                kwargs.update({extension: manager.all()})
        return super(VideoDetail, self).get_context_data(
            sources=self.object.sources.all(),
            **kwargs
        )
