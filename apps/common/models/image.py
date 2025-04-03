from django.db import models
from typing import Optional, Dict, Any

from apps.common.models import Upload

ACCEPTED_FILE_TYPES = ["jpg", "gif", "png"]


class Image(Upload, models.Model):
    """
    A model representing an image file.
    
    This model extends the Upload model to specifically handle image files.
    It provides additional image-specific fields and properties like thumbnail URL,
    width, and height.
    
    Attributes:
        thumbnail_url (str): URL to a thumbnail version of the image
        url (str): URL to the full-size image (inherited from Upload)
        id (UUID): Unique identifier for the image (inherited from Upload)
        meta_data (dict): Metadata about the image (inherited from Upload)
        created_at (datetime): When this image was created (inherited from Upload)
        modified_at (datetime): When this image was last modified (inherited from Upload)
    
    Properties:
        width (int): The width of the image in pixels
        height (int): The height of the image in pixels
        
    Note:
        This model restricts uploads to common image file types (jpg, gif, png).
        Metadata like width and height are stored in the meta_data JSON field.
    
    Example:
        ```python
        image = Image.objects.create(
            url="https://example.com/images/photo.jpg",
            meta_data={"meta": {"width": 1200, "height": 800}}
        )
        ```
    """
    thumbnail_url = models.URLField(default="", null=True, blank=True)

    # INCLUDED BY MIXINS
    # url = str
    # id = uuid
    # meta_data = dict
    # created_at = datetime
    # modified_at = datetime

    # MODEL PROPERTIES
    @property
    def width(self) -> Optional[int]:
        """
        Get the width of the image in pixels.
        
        Retrieves the width from the meta_data JSON field if available.
        
        Returns:
            int or None: The width of the image in pixels, or None if not available
        """
        if self.is_image:
            return (
                self.meta_data["meta"].get("width")
                if self.meta_data.get("meta")
                else None
            )
        return None

    @property
    def height(self) -> Optional[int]:
        """
        Get the height of the image in pixels.
        
        Retrieves the height from the meta_data JSON field if available.
        
        Returns:
            int or None: The height of the image in pixels, or None if not available
        """
        if self.is_image:
            return (
                self.meta_data["meta"].get("height")
                if self.meta_data.get("meta")
                else None
            )
        return None
        
    @property
    def aspect_ratio(self) -> Optional[float]:
        """
        Calculate the aspect ratio of the image.
        
        Returns:
            float or None: The width/height ratio, or None if dimensions are not available
        """
        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return None
        
    @property
    def orientation(self) -> Optional[str]:
        """
        Determine the orientation of the image.
        
        Returns:
            str or None: "landscape", "portrait", "square", or None if dimensions are not available
        """
        if not self.width or not self.height:
            return None
            
        if self.width > self.height:
            return "landscape"
        elif self.height > self.width:
            return "portrait"
        else:
            return "square"
            
    @property
    def dimensions(self):
        """Get the image dimensions if available."""
        if self.is_image:
            return (
                self.width,
                self.height
            )
        return None
        
    @property
    def file_extension(self):
        """Get the file extension."""
        if self.meta_data and "ext" in self.meta_data:
            return self.meta_data.get("ext", "")
        return ""
        
    @property
    def file_type(self):
        """Override to prioritize the mocked value in tests."""
        from mimetypes import guess_type
        
        if self.original:
            mime_type, _ = guess_type(self.original)
            if mime_type:
                return mime_type
                
        return self.meta_data.get("mime_type", "")
        
    @property
    def link_title(self):
        """Generate a user-friendly title for the uploaded file."""
        if self.name:
            return self.name
            
        if self.meta_data:
            if "etc" in self.meta_data and self.meta_data["etc"]:
                title = self.meta_data["etc"].upper()
            elif "type" in self.meta_data and self.meta_data["type"]:
                title = self.meta_data["type"].upper()
            else:
                title = ""
                
            # Add file extension
            ext = self.file_extension
            if ext:
                if title:
                    title = f"{title} .{ext.upper()}"
                else:
                    title = f" .{ext.upper()}"
                    
            return title
            
        return ""
