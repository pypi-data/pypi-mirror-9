import os
from django.db.models import Model
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings

__author__ = "Dmitry Simonov"
__email__ = "demalf@gmail.com"
__license__ = "GPL"


def render(self, template=None):
    """
    Render single model to its html representation.

    You may set template path in render function argument,
        or model's variable named 'template_path',
        or get default name: $app_label$/models/$model_name$.html

    Settings:
    * MODEL_RENDER_DEFAULT_EXTENSION
        set default template extension. Usable if you use jinja or others.

    :param template: custom template_path
    :return: rendered model html string
    """
    template_path = template or getattr(
        self, "template_path", None) or os.path.join(
        self._meta.app_label,
        'models',
        self._meta.object_name.lower() + "." + getattr(
            settings, "MODEL_RENDER_DEFAULT_EXTENSION", "html"))
    rendered = render_to_string(template_path, {'model': self})
    return mark_safe(rendered)

Model.template_path = None
Model.render = render
