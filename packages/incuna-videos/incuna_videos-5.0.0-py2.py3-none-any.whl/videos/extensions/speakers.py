from django.db import models
from django.utils.translation import ugettext_lazy as _
from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        self.model.add_to_class(
            'speakers',
            models.ManyToManyField('videos.Speaker', null=True, blank=True))

    def handle_modeladmin(self, modeladmin):
        fields = ['speakers']
        modeladmin.extend_list(
            'list_display_filter',
            fields,
        )
        modeladmin.extend_list(
            'filter_horizontal',
            fields,
        )
        modeladmin.add_extension_options(_('Speakers'), {
            'fields': fields,
            'classes': ('collapse',),
        })
