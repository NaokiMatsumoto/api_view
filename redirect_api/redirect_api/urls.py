from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('nishi/', admin.site.urls),
    path('api/', include('api.urls')),
    path("seminars/", include("seminar.urls")),
    path("account/", include("account.urls")),
]
