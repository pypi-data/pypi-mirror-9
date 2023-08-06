from django.db import models
from django.utils.translation import ugettext_lazy as _
from feincms import extensions
from feincms.module.page.models import Page


class Extension(extensions.Extension):
    """
    Add a prepared date value to the FeinCMS `page.Page` model.
    If the page has no value set then the value is taken from nearest ancestor
    page (based on `_cached_url` path) that has a value.
    """

    def handle_model(self):
        self.model.add_to_class(
            '_prepared_date',
            models.TextField(
                'Date of Preparation',
                default='',
                blank=True,
                help_text=_('If not set the value from the closest parent page will be used.'),
            ),
        )

        def getter(obj):
            if obj._prepared_date:
                return obj._prepared_date

            # Find the best matching parent page (based on url) that has a _prepared_date
            tokens = obj.get_absolute_url().strip('/').split('/')
            paths = ['/'] + ['/%s/' % '/'.join(tokens[:i]) for i in range(1, len(tokens) + 1)]
            try:
                return Page.objects.apply_active_filters(
                    Page.objects.exclude(
                        _prepared_date=''
                    ).filter(
                        _cached_url__in=paths
                    ).extra(
                        select={'_url_length': 'LENGTH(_cached_url)'}
                    ).order_by(
                        '-_url_length'
                    )
                )[0]._prepared_date
            except IndexError:
                return ''

        def setter(obj, value):
            obj._prepared_date = value

        self.model.prepared_date = property(getter, setter)

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options(_('Date of Preparation'), {
            'fields': ('_prepared_date',),
            'classes': ('collapse',),
        })
