from feincms.content.medialibrary.models import MediaFileContent
from feincms.content.richtext.models import RichTextContent
from feincms.content.section.models import SectionContent


class JsonRichTextContent(RichTextContent):
    class Meta(RichTextContent.Meta):
        abstract = True

    def json(self, **kwargs):
        """Return a json serializable dictionary containing the content."""
        return {'html': self.text}


def mediafile_data(mediafile):
    """Return json serializable data for the mediafile."""
    if mediafile is None:
        return None
    return {
        'url': mediafile.file.url,
        'type': mediafile.type,
        'created': mediafile.created,
        'copyright': mediafile.copyright,
        'file_size': mediafile.file_size,
    }


class JsonSectionContent(SectionContent):
    class Meta(SectionContent.Meta):
        abstract = True

    def json(self, **kwargs):
        """Return a json serializable dictionary containing the content."""
        return {
            'title': self.title,
            'html': self.richtext,
            'mediafile': mediafile_data(self.mediafile),
        }


class JsonMediaFileContent(MediaFileContent):
    class Meta(MediaFileContent.Meta):
        abstract = True

    def json(self, **kwargs):
        """Return a json serializable dictionary containing the content."""
        return mediafile_data(self.mediafile)
