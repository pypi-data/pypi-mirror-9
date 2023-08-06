from django.views.generic import TemplateView

from .factories import PageFactory
from .utils import RenderedContentTestCase


class DummyView(TemplateView):
    template_name = 'feincms_extensions/navigation.html'


class DummyViewCustomTemplate(TemplateView):
    template_name = 'navigation_test.html'


class PageMixin:
    def setUp(self):
        self.page = PageFactory.create(in_navigation=True, override_url='/')


class TestNoPage(RenderedContentTestCase):
    view = DummyView

    def test_failing(self):
        """At least one page is required when using the Page module from FeinCMS."""
        with self.assertRaises(AttributeError):
            self.access_view_and_render_response()


class TestPageMenuNavigation(PageMixin, RenderedContentTestCase):
    view = DummyView

    def test_menu(self):
        response = self.access_view_and_render_response()

        template = """
        <ul id="top-level">
            <li class=" selected">
                <span><a href="{}">{}</a></span>
            </li>
        </ul>
        """
        expected = template.format(self.page.override_url, self.page.title)
        self.assertHTMLEqual(response, expected)


class TestPageMenuCustomNavigation(PageMixin, RenderedContentTestCase):
    view = DummyViewCustomTemplate

    def test_nav_id(self):
        response = self.access_view_and_render_response()

        template = """
        <ul id="new-id">
            <li class=" selected">
                <span><a href="{}">{}</a></span>
            </li>
        </ul>
        """
        expected = template.format(self.page.override_url, self.page.title)
        self.assertHTMLEqual(response, expected)

    def test_depth(self):
        child = PageFactory.create(
            in_navigation=True,
            override_url='/child-page/',
            parent=self.page,
        )

        response = self.access_view_and_render_response()

        template = """
        <ul id="new-id">
            <li class="selected has-children">
                <span><a href="{}">{}</a></span>
            </li>
            <ul>
                <li class=" ">
                    <span><a href="{}">{}</a></span>
                </li>
            </ul>
        </ul>
        """
        expected = template.format(
            self.page.override_url,
            self.page.title,
            child.override_url,
            child.title,
        )
        self.assertHTMLEqual(response, expected)

    def test_depth_not_rendered(self):
        child = PageFactory.create(
            in_navigation=True,
            override_url='/child-page/',
            parent=self.page,
        )

        grand_child = PageFactory.create(
            in_navigation=True,
            override_url='/grand-child-page/',
            parent=child,
        )

        response = self.access_view_and_render_response()
        self.assertNotIn(grand_child.title, response)
