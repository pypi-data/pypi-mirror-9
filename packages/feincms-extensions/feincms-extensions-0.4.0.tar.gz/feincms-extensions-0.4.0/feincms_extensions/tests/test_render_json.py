import unittest

import django
from django.core import checks
from django.test import TestCase, TransactionTestCase
from feincms.content.richtext.models import RichTextContent
from mock import patch, MagicMock

from .factories import DummyFactory
from .models import Dummy


skip_if_checks_unavailable = unittest.skipIf(
    django.VERSION < (1, 7),
    'Checks only available in django>=1.7',
)


class TestExtension(TestCase):
    def test_json_regions(self):
        request = MagicMock()

        dummy = DummyFactory.create()
        json_path = 'feincms_extensions.tests.content.TestContent.json'
        expected_dict = {'foo': 'bar'}
        with patch(json_path) as json:
            json.return_value = expected_dict
            self.assertEqual(
                dummy.render_json(request),
                {'body': [expected_dict]},
            )

        json.assert_called_once_with(request=request)


class TestExtensionChecks(TransactionTestCase):
    @skip_if_checks_unavailable
    def test_check_content_types_json(self):
        rich_text_content = Dummy.create_content_type(RichTextContent)

        message = (
            'Feincms content has no `json` method, but the `render_json` ' +
            'extension is active for model `{}`.'
        ).format(Dummy)
        expected = [
            checks.Error(
                message,
                obj=rich_text_content,
                id='feincms_extensions.E001',
            ),
        ]
        self.assertEqual(Dummy.check(), expected)
