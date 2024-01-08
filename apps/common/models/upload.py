from django.db import models
from mimetypes import guess_type
from ..behaviors import Timestampable


class Upload(Timestampable, models.Model):
    """
    A model representing an uploaded file, including its metadata and properties.

    This model stores information about uploaded files, including the original URL,
    name, thumbnail, and various metadata. It also provides properties to access
    specific attributes such as file type, dimensions, and extensions.

    Attributes:
        original (str): The original URL of the uploaded file.
        name (str): The name of the file, if available.
        thumbnail (str): The URL of the thumbnail image, if available.
        meta_data (Dict): A JSON field containing additional metadata about the file.

    Properties:
        file_type (str): The type of the file, extracted from the metadata.
        is_image (bool): A flag indicating whether the file is an image.
        is_pdf (bool): A flag indicating whether the file is a PDF.
        width (int): The width of the image, if applicable.
        height (int): The height of the image, if applicable.
        file_extension (str): The file extension, extracted from the metadata.
        link_title (str): A formatted title for the link, based on the name, type, and extension.

    Note:
        The properties `width` and `height` are only applicable if the file is an image.
        The `meta_data` field is expected to contain keys such as 'type', 'ext', 'meta', and 'etc',
        depending on the specific use case and the information available about the uploaded file.
    """

    original = models.URLField(default="")
    name = models.CharField(max_length=50, blank=True, null=True)
    thumbnail = models.URLField(default="", blank=True, null=True)
    meta_data = models.JSONField(blank=True, null=True)

    @property
    def mime_type(self):
        return self.meta_data.get("mime_type", "")

    @property
    def file_type(self):
        (mime_type, encoding) = guess_type(self.original)
        return mime_type or self.mime_type

    @property
    def is_image(self):
        return True if "image" in self.file_type else False

    @property
    def is_pdf(self):
        return True if "pdf" in self.file_type else False

    @property
    def width(self):
        if self.is_image:
            return (
                self.meta_data["meta"].get("width")
                if self.meta_data.get("meta")
                else None
            )

    @property
    def height(self):
        if self.is_image:
            return (
                self.meta_data["meta"].get("height")
                if self.meta_data.get("meta")
                else None
            )

    @property
    def file_extension(self):
        return self.meta_data.get("ext", "")

    @property
    def dimensions(self):
        if self.is_image or self.is_video:
            return (
                (
                    self.meta_data["meta"].get("width"),
                    self.meta_data["meta"].get("height"),
                )
                if self.meta_data.get("meta")
                else (None, None)
            )

    @property
    def link_title(self):
        if self.name:
            title = self.name
        elif "etc" in self.meta_data:
            title = (self.meta_data["etc"] or "").upper()
        else:
            title = (
                (self.meta_data["type"] or "").upper()
                if "type" in self.meta_data
                else ""
            )
        if "ext" in self.meta_data:
            title = title + " .%s" % (self.meta_data["ext"] or "").upper()
        return title
