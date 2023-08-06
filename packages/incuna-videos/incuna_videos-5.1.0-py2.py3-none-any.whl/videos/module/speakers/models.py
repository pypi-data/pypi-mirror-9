from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Speaker(models.Model):
    """A person who features in a video"""
    name = models.CharField(max_length=127)
    slug = models.SlugField(
        max_length=127,
        help_text=(
            "This will be automatically generated from the name, and is used" +
            "in the speaker's website address",
        ),
        editable=True,
        unique=True,
    )

    class Meta:
        app_label = 'videos'

    def __str__(self):
        return self.name
