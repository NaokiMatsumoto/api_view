from .models import Lesson
from rest_framework import serializers
from django.shortcuts import get_object_or_404


class LessonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'url', 'default_url',)
