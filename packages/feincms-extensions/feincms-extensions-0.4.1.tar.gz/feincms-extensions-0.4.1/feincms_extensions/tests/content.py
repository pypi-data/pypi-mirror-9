from django.db import models


class TestContent(models.Model):
    """A stub feincms content type"""
    class Meta:
        abstract = True

    def render(self, **kwargs):
        return ''

    def json(self, **kwargs):
        return ''
