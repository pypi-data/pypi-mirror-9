from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from feincms.module.page.admin import PageAdmin
from feincms.module.page.models import Page
import mock

from .factories import PageFactory


class TestExtension(TestCase):
    def test_prepared_date_empty(self):
        page = PageFactory.create()

        self.assertEqual(page.prepared_date, '')

    def test_set_prepared_date(self):
        prepared_date = 'Sample data'
        page = PageFactory.create()
        page.prepared_date = prepared_date
        self.assertEqual(page.prepared_date, prepared_date)

    def test_prepared_date_parent(self):
        prepared_date = 'Sample data'
        parent = PageFactory.create(prepared_date=prepared_date, slug='a')
        page = PageFactory.create(parent=parent, slug='b')

        self.assertEqual(page.prepared_date, prepared_date)

    def test_prepared_date_override_url(self):
        prepared_date = 'Sample data'
        PageFactory.create(prepared_date=prepared_date, override_url='/')
        page = PageFactory.create(slug='page')

        self.assertEqual(page.prepared_date, prepared_date)

    def test_handle_modeladmin(self):
        page_admin = PageAdmin(Page, AdminSite())
        form = page_admin.get_form(mock.Mock())()
        self.assertIn('_prepared_date', form._meta.fields)
