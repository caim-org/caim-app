import logging

from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from .templatetags.caim_helpers import image_resize

logger = logging.getLogger(__name__)


class AdminImageWidget(forms.ClearableFileInput):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it has one.
    """

    def render(self, name, value, attrs=None, **kwargs):
        output = super().render(name, value, attrs, **kwargs)
        output = output.replace(
            "label>", "span>"
        )  # Using <label> causes a layout issue with the clear button
        if value and hasattr(value, "url"):
            try:
                mini_url = image_resize(value.url, "80x80")
            except Exception as e:
                logger.warning("Unable to get the thumbnail", exc_info=e)
            else:
                try:
                    # Not beautiful code, but prepend the image ina floating div
                    output = (
                        '<div style="float:left">'
                        '<a style="width:80px;display:block;margin:0 8px 0 0" class="thumbnail" '
                        'target="_blank" href="%s">'
                        '<img src="%s"></a></div>%s'
                    ) % (value.url, mini_url, output)
                except (AttributeError, TypeError):
                    pass
        return mark_safe(output)


class AdminImageMixin:
    """
    This is a mix-in for InlineModelAdmin subclasses to make ``ImageField``
    show nicer form widget
    """

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.ImageField):
            return db_field.formfield(widget=AdminImageWidget)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
