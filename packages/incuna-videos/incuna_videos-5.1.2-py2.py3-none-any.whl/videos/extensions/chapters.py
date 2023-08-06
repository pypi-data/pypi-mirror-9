from django.contrib import admin
from videos.module.chapters.models import Chapter
from feincms import extensions


class ChapterInline(admin.TabularInline):
    fields = ('title', 'timecode', 'preview')
    model = Chapter
    extra = 1


class Extension(extensions.Extension):
    def handle_model(self):
        pass

    def handle_modeladmin(self, modeladmin):
        modeladmin.extend_list('inlines', [ChapterInline])
