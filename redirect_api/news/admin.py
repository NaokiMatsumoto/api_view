from django.contrib import admin
from .models import NewsArticle, NewsSource, Region

admin.site.register(NewsSource)
admin.site.register(NewsArticle)
admin.site.register(Region)