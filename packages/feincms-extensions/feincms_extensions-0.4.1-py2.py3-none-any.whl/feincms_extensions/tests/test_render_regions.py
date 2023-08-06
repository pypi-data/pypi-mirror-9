from django.test import TestCase
from mock import patch, MagicMock

from .factories import DummyFactory


class TestExtension(TestCase):
    def test_rendered_regions(self):
        request = MagicMock()

        dummy = DummyFactory.create()
        render_path = 'feincms_extensions.tests.content.TestContent.render'
        with patch(render_path) as render:
            render.return_value = ''
            dummy.rendered_regions(request)

        render.assert_called_once_with(request=request)
