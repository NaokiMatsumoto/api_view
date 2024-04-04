from django.urls import path
from .views import NewsSourceListView, hide_articles, NewsSourceListRedirectView, ToggleFavoriteView, FavoriteListView

app_name = 'news'

urlpatterns = [
    path('', NewsSourceListRedirectView.as_view(), name='news_list_redirect'),
    path('<int:year>/<int:month>/<int:day>/', NewsSourceListView.as_view(), name='news_list'),
    path('hide-articles/<int:year>/<int:month>/<int:day>/', hide_articles, name='hide_articles'),
    path('toggle_favorite/<int:article_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorite_list'),
]