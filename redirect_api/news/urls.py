from django.urls import path
from .views import (
    StarupNewsSourceListView, OriginalNewsSourceListView, hide_articles, 
    StartupNewsSourceListRedirectView, OriginalNewsSourceListRedirectView, ToggleFavoriteView, 
    FavoriteListView, CommentCreateUpdateView,
    CommentDeleteView,
)
app_name = 'news'

urlpatterns = [
    path('', OriginalNewsSourceListRedirectView.as_view(), name='news_list_redirect'),
    path('startup', StartupNewsSourceListRedirectView.as_view(), name='news_list_startup_redirect'),
    path('<int:year>/<int:month>/<int:day>/', OriginalNewsSourceListView.as_view(), name='news_list'),
    path('<int:year>/<int:month>/<int:day>/<int:region_id>/', OriginalNewsSourceListView.as_view(), name='news_list_by_region'),
    path('startup/<int:year>/<int:month>/<int:day>/', StarupNewsSourceListView.as_view(), name='news_list_by_startup'),
    path('startup/<int:year>/<int:month>/<int:day>/<int:region_id>/', StarupNewsSourceListView.as_view(), name='news_list_by_region_and_startup'),
    path('hide-articles/<int:year>/<int:month>/<int:day>/', hide_articles, name='hide_articles'),
    path('toggle_favorite/<int:article_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorite_list'),
    path('comment/<int:article_id>/', CommentCreateUpdateView.as_view(), name='comment_create_update'),
    path('comment/delete/<int:article_id>/', CommentDeleteView.as_view(), name='comment_delete'),
]