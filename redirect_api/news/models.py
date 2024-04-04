from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class NewsSource(models.Model):
    url = models.URLField(unique=True)
    host = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255)
    japanese_name = models.CharField(max_length=255, default='')
    is_japanese_site = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    news_source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    url = models.URLField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    japanese_title = models.CharField(max_length=255, default='')
    content = models.TextField(default='')
    japanese_content = models.CharField(max_length=255, default='')
    shown = models.BooleanField(default=True)
    is_scraped = models.BooleanField(default=False)
    published_at = models.DateField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
