from django.db import models
from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        self.model.add_to_class(
            'sub_title',
            models.CharField(max_length=255, null=True, blank=True))

    def handle_modeladmin(self, modeladmin):
        modeladmin.extend_list(
            'search_fields',
            ['sub_title'],
        )
        modeladmin.add_extension_options('sub_title')
