from django import forms
from django.contrib import admin
from feincms.extensions import ExtensionModelAdmin

from .models import Source, Video


class BaseSourceFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        super(BaseSourceFormSet, self).clean()

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        if not any(filter(lambda form: getattr(form, 'cleaned_data', None), self.forms)):
            msg = 'Please specify at least one {0}'.format(self.model._meta.verbose_name)
            raise forms.ValidationError(msg)


class SourceInline(admin.TabularInline):
    extra = 1
    fields = ('file', 'type')
    model = Source
    formset = BaseSourceFormSet


class VideoAdmin(ExtensionModelAdmin):
    inlines = [SourceInline]
    list_display = ['title', 'preview', 'created', 'recorded']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (
            '',
            {
                'fields': ['title', 'slug', 'preview', 'length', 'recorded'],
            }
        )
    ]


admin.site.register(Video, VideoAdmin)
