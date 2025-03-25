from django.db import models

from apps.common.behaviors import timestampable


class PromptTemplate(timestampable.Timestampable, models.Model):
    """
    A template for prompts that can be used with variable substitutions.
    Stores the template text with placeholders for variables.

    Example template_text:
    "Hello, {{name}}! How can I help you today with {{topic}}?"
    """
    name = models.CharField(max_length=255)
    template_text = models.TextField()
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Prompt Template"
        verbose_name_plural = "Prompt Templates"
        ordering = ["-modified_at"]

    def __str__(self):
        return f"{self.name} (v{self.version})" if self.version else self.name

    def render(self, variables=None):
        """
        Render the template with the provided variables.

        Args:
            variables (dict): Dictionary of variables to substitute in the template

        Returns:
            str: The rendered template text
        """
        if not variables:
            return self.template_text

        rendered_text = self.template_text
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            rendered_text = rendered_text.replace(placeholder, str(value))

        return rendered_text
