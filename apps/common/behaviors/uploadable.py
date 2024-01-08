import json
import uuid
from django.db import models
from typing import Optional


class Uploadable(models.Model):
    """
    A mixin for use with models that require file upload functionality.

    This abstract model encapsulates common attributes related to file uploads and can be used
    in various models that require these features. It provides a unique identifier for each upload,
    a URL to access the uploaded file, and a flexible JSON field to store any relevant metadata.

    Attributes:
        id (UUID): A unique identifier for the upload, generated automatically using UUID version 4.
            This field is the primary key and is not editable.

        url (str): A URL to access the uploaded file. It can be used to retrieve or display the file
            in different parts of the application.

        meta_data (Dict[str, Any]): A dictionary to store unstructured metadata related to the file.
            This can include details like file size, compression type, resolution,
            or any other that might be relevant to the specific use case.
            Feel free to use this as a dumping grounds for meta_data
            that a 3rd party image hosting or processing service might provide.
            (just make sure that 3rd party data is json serializable)

    Note:
        This model is abstract and should be used as a mixin in other models.
        The `meta_data` field is intentionally flexible to accommodate various metadata requirements.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(default="")
    meta_data = models.JSONField(default=dict)  # type: Dict[str, Any]

    class Meta:
        abstract = True
