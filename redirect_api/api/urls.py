from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LessonViewSet

router = DefaultRouter()
router.register('lesson', LessonViewSet, basename='lesson')

urlpatterns = [
    path('', include(router.urls))
]