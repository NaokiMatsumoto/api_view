from django.urls import path
from .views import MemoListView, MemoDeleteView, MemoUpdateView, MemoCreateView

app_name = 'memo'

urlpatterns = [
    path('memo/', MemoListView.as_view(), name='memo_list'),
    path('memos/<int:pk>/', MemoListView.as_view(), name='memo_list'),
    path('memos/create/', MemoCreateView.as_view(), name='memo_create'),
    path('memos/<int:pk>/update/', MemoUpdateView.as_view(), name='memo_update'),
    path('memos/<int:pk>/delete/', MemoDeleteView.as_view(), name='memo_delete'),
]
