from django.urls import path
from .views import NewsSourceListView, hide_articles, NewsSourceListRedirectView

urlpatterns = [
    path('', NewsSourceListRedirectView.as_view(), name='news_list_redirect'),
    path('<int:year>/<int:month>/<int:day>/', NewsSourceListView.as_view(), name='news_list'),
    path('hide-articles/<int:year>/<int:month>/<int:day>/', hide_articles, name='hide_articles'),
]