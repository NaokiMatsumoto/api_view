from django.db import models


class Lesson(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=300)
    description = models.TextField()
    url = models.URLField(null=True)
    default_url = models.URLField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
