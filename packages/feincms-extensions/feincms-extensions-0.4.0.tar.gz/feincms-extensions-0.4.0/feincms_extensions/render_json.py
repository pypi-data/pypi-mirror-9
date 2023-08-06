from django.core import checks
from feincms import extensions


class Extension(extensions.Extension):
    def handle_model(self):
        cls = self.model

        def render_json(self, request):
            """Render the feincms regions into a dictionary."""

            def region_data(region):
                content_list = getattr(self.content, region.key)
                return [content.json(request=request) for content in content_list]

            regions = self.template.regions
            return {region.key: region_data(region) for region in regions}

        cls.add_to_class('render_json', render_json)

        @classmethod
        def check(cls, **kwargs):
            errors = super(self.model, cls).check(**kwargs)
            errors.extend(cls._check_json_method())
            return errors

        @classmethod
        def _check_json_method(cls, **kwargs):
            """Check all registered content types have a `.json` method."""
            message = (
                'Feincms content has no `json` method, but the ' +
                '`render_json` extension is active for model `{}`.'
            ).format(cls)
            for content_type in cls._feincms_content_types:
                if not hasattr(content_type, 'json'):
                    yield checks.Error(
                        message,
                        obj=content_type,
                        id='feincms_extensions.E001',
                    )

        cls.add_to_class('check', check)
        cls.add_to_class('_check_json_method', _check_json_method)
