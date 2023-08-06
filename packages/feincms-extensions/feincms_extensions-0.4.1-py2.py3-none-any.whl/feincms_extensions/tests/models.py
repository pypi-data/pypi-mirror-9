from feincms.models import create_base_model
from feincms.module.page.models import Page

from .content import TestContent
from .. import content_types


TYPE_CHOICES = (
    ('block', 'Block'),
)


class Dummy(create_base_model()):
    """A fake class for holding content"""


Dummy.register_regions(('body', 'Main'))
Dummy.create_content_type(TestContent)
Dummy.create_content_type(content_types.JsonRichTextContent)
Dummy.create_content_type(
    content_types.JsonMediaFileContent,
    TYPE_CHOICES=TYPE_CHOICES,
)
Dummy.create_content_type(
    content_types.JsonSectionContent,
    TYPE_CHOICES=TYPE_CHOICES,
)
Dummy.register_extensions(
    'feincms_extensions.render_regions',
    'feincms_extensions.render_json',
)

Page.register_templates({
    'key': 'key',
    'title': 'Title',
    'path': 'base.html',
    'regions': (
        ('body', 'Main'),
    ),
})
Page.register_extensions(
    'feincms_extensions.prepared_date',
)
