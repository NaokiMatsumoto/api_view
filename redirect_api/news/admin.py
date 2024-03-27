from django.contrib import admin
from .models import NewsArticle, NewsSource

admin.site.register(NewsSource)
admin.site.register(NewsArticle)
