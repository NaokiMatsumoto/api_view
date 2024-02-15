from rest_framework.response import Response
from rest_framework import viewsets
from django.http import HttpResponseRedirect, Http404
from .models import Lesson
from .serializers import LessonSerializer
from datetime import datetime

lessons = {}

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    # 詳細画面
    def retrieve(self, request, *args, **kwargs):
        # 現在の日付を取得
        now = datetime.now()
        # 日付に基づいてリダイレクトURLに使用する日付の部分を決定
        day = '01'
        if 11 <= now.day < 20:
            day = '11'
        elif now.day >= 20:
            day = '21'
        url_date = now.strftime('%Y%m') + day
        # requestからpkを取得し、整数型として扱う
        pk = kwargs.get('pk')
        # pkをキーにしてlessonsに格納
        if pk not in lessons:
            instance = self.get_object()
            lessons[pk] = instance
        else:
            instance = lessons[pk]
        
        # リダイレクトURLを決定。instance.urlがNoneの場合は、instance.default_urlを使用
        redirect_url = instance.url or instance.default_url
        # redirect_urlがNoneの場合は404エラーを発生
        if redirect_url is None:
            raise Http404("ページが見つかりませんでした。")
        
        # yyyymmddを適切な値に置換してリダイレクト
        redirect_url = redirect_url.replace('yyyymmdd', url_date)
        return HttpResponseRedirect(redirect_url)
