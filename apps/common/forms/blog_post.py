from django import forms
from apps.common.models import BlogPost


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""
    
    class Meta:
        model = BlogPost
        fields = [
            "title",
            "subtitle",
            "content",
            "featured_image",
            "reading_time_minutes",
            "tags",
            "address",
            "is_author_anonymous",
        ]
        
    def clean(self):
        """Validate required fields."""
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")
        
        if not title:
            self.add_error("title", "Title is required")
        
        if not content:
            self.add_error("content", "Content is required")
        
        return cleaned_data