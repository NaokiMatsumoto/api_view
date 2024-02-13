from rest_framework.response import Response
from rest_framework import viewsets
from django.http import HttpResponseRedirect
from .models import Lesson
from .serializers import LessonSerializer
from django.http import Http404
from datetime import datetime


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    model = Lesson
    serializer_class = LessonSerializer
    
    # 詳細画面
    def retrieve(self, request, *args, **kwargs):
        # 現在の日付を取得
        now = datetime.now()
        # 日付に基づいてリダイレクトURLに使用する日付の部分を決定
        day = '01' if now.day < 16 else '16'
        url_date = now.strftime('%Y%m') + day
        
        # オブジェクトを取得
        instance = self.get_object()
        
        # リダイレクトURLを決定。instance.urlがNoneの場合は、instance.default_urlを使用
        redirect_url = instance.url or instance.default_url
        
        # redirect_urlがNoneの場合は404エラーを発生
        if redirect_url is None:
            raise Http404("ページが見つかりませんでした。")
        
        # yyyymmddを適切な値に置換してリダイレクト
        redirect_url = redirect_url.replace('yyyymmdd', url_date)
        return HttpResponseRedirect(redirect_url)
