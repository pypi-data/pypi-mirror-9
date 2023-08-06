import datetime

from django.test import TestCase

from . import factories
from .models import Dummy
from .. import content_types


class TestJsonRichTextContent(TestCase):
    model = Dummy.content_type_for(content_types.JsonRichTextContent)

    def test_json(self):
        """A JsonRichTextContent can be rendered to json."""
        text = 'Rich Text'
        content = self.model(region='body', text=text)
        self.assertEqual(content.json(), {'html': text})


class TestJsonSectionContent(TestCase):
    model = Dummy.content_type_for(content_types.JsonSectionContent)

    def test_json(self):
        """A JsonSectionContent can be rendered to json."""
        title = 'Section 1'
        richtext = 'Rich Text'
        image_type = 'image'
        copyright = 'Incuna'
        created = datetime.datetime(year=2015, month=3, day=1)

        image = factories.MediaFileFactory.build(
            type=image_type,
            copyright=copyright,
            created=created,
        )
        content = self.model(
            region='body',
            title=title,
            richtext=richtext,
            mediafile=image,
        )

        expected = {
            'title': title,
            'html': richtext,
            'mediafile': {
                'url': image.file.url,
                'type': image_type,
                'created': created,
                'copyright': copyright,
                'file_size': image.file.size,
            },
        }
        self.assertEqual(content.json(), expected)

    def test_json_no_mediafile(self):
        """A JsonSectionContent can be rendered to json."""
        title = 'Section 1'
        richtext = 'Rich Text'

        content = self.model(
            region='body',
            title=title,
            richtext=richtext,
            mediafile=None,
        )

        expected = {
            'title': title,
            'html': richtext,
            'mediafile': None,
        }
        self.assertEqual(content.json(), expected)


class TestJsonMediaFileContent(TestCase):
    model = Dummy.content_type_for(content_types.JsonMediaFileContent)

    def test_json(self):
        """A JsonMediaFileContent can be rendered to json."""
        image_type = 'image'
        copyright = 'Incuna'
        created = datetime.datetime(year=2015, month=3, day=1)

        image = factories.MediaFileFactory.build(
            type=image_type,
            copyright=copyright,
            created=created,
        )
        content = self.model(region='body', mediafile=image)

        expected = {
            'url': image.file.url,
            'type': image_type,
            'created': created,
            'copyright': copyright,
            'file_size': image.file.size,
        }
        self.assertEqual(content.json(), expected)
