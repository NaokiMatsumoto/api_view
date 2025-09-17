from django.db import models


class Lesson(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    url = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    default_url = models.URLField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}({self.id}): {self.url}"