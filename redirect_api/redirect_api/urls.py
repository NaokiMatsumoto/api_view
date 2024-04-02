from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('nishi/', admin.site.urls),
    path('api/', include('api.urls')),
    path('news/', include('news.urls')),
    path('accounts/', include('accounts.urls')),
    path('memo/', include('memo.urls'))
]
