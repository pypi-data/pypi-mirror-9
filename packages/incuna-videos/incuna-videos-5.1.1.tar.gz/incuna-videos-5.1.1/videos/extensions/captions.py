from django.db import models
from django.utils.translation import ugettext_lazy as _
from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        captions_field = models.FileField(
            upload_to='videos/captions/',
            null=True,
            blank=True,
            help_text=_('Captions (subtitles) file.'),
        )
        self.model.add_to_class('captions_file', captions_field)

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options('captions_file')
