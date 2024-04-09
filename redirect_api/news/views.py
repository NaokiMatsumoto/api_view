from django.views.generic import ListView, RedirectView, View
from django.db.models import Prefetch, Exists, OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from calendar import monthrange
from django.utils import timezone
from django.http import JsonResponse
from .models import NewsSource, NewsArticle, Favorite, Region, Comment
from datetime import datetime, date



class NewsSourceListRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        today = date.today()
        return reverse('news:news_list', kwargs={
            'year': today.year,
            'month': today.month,
            'day': today.day
        })

class NewsSourceListView(LoginRequiredMixin, ListView):
    model = NewsSource
    template_name = 'news/news_list.html'
    context_object_name = 'news_sources'
    published_at = None
    region_id = None
    
    def adjust_date(self, year, month, day):
        # 0日の場合は、前月（前年）に移動する
        _, last_day = monthrange(year, month)
        if day == 0:
            month, year, day = self.move_to_previous_month(month, year)

        # last_day日以上の場合は、翌月（翌年）に移動する
        elif day > last_day:
            month, year, day = self.move_to_next_month(month, year)

        # 無効な日付の場合は、適切な日付に調整する
        try:
            published_at = datetime(year, month, day)
        except ValueError:
            _, last_day = monthrange(year, month)
            day = min(day, last_day)
            published_at = datetime(year, month, day)

        # 未来の日付の場合は、Noneを返す
        if published_at.date() > datetime.now().date():
            return None

        return year, month, day

    def move_to_previous_month(self, month, year):
        month -= 1
        if month == 0:
            year -= 1
            month = 12
        _, last_day = monthrange(year, month)
        return month, year, last_day

    def move_to_next_month(self, month, year):
        month += 1
        if month == 13:
            year += 1
            month = 1
        return month, year, 1

    def redirect_to_current_date(self):
        current_date = timezone.now().date()
        return redirect(reverse('news:news_list', args=[current_date.year, current_date.month, current_date.day]))


    def get_queryset(self):
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        day = int(self.kwargs['day'])
        adjusted_date = self.adjust_date(year, month, day)
        self.region_id = self.kwargs.get('region_id')
        
        if adjusted_date is None:
            datetime_now = timezone.now()
            year, month, day = datetime_now.year, datetime_now.month, datetime_now.day
        else:
            year, month, day = adjusted_date
        
        self.published_at = datetime(year, month, day)
        queryset = super().get_queryset().prefetch_related(
            Prefetch(
                'newsarticle_set',
                queryset=NewsArticle.objects.filter(shown=True, published_at=self.published_at).annotate(
                    is_favorite=Exists(Favorite.objects.filter(user=self.request.user, article=OuterRef('pk'))),
                    comment=Subquery(
                        Comment.objects.filter(
                            user=self.request.user,
                            article=OuterRef('pk')
                        ).values('content')[:1]
                    ),
                ),
                to_attr='published_articles'
            )
        ).annotate(
            representative_region=Subquery(
                NewsSource.regions.through.objects.filter(
                    newssource_id=OuterRef('pk')
                ).values('region__japanese_name')[:1]
            )
        )
        
        if self.region_id:
            queryset = queryset.filter(regions__id=self.region_id).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.published_at is None:
            context['published_at'] = timezone.now().date()
        else:
            context['published_at'] = self.published_at
        if self.region_id:
            context['region_id'] = self.region_id
        context['regions'] = Region.objects.all()
        return context


class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'news/favorite_list.html'
    context_object_name = 'favorites'
    paginate_by = 50

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).annotate(
            comment=Subquery(
                Comment.objects.filter(
                    user=self.request.user,
                    article=OuterRef('article_id')
                ).values('content')[:1]
            )
        ).order_by('-article__published_at')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_article_ids = self.object_list.values_list('article_id', flat=True)
        context['favorite_article_ids'] = list(favorite_article_ids)
        return context

class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, article_id):
        article = get_object_or_404(NewsArticle, id=article_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, article=article)
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
        
        return JsonResponse({'is_favorite': is_favorite})

@require_POST
@login_required
def hide_articles(request, year, month, day):
    article_ids = request.POST.get('article_ids', '').split(',')
    NewsArticle.objects.filter(id__in=article_ids).update(shown=False)
    return redirect(reverse('news:news_list', kwargs={
        'year': year,
        'month': month,
        'day': day
    }))

class CommentCreateUpdateView(LoginRequiredMixin, View):
    
    def post(self, request, article_id):
        content = request.POST.get('content')
        if content:
            comment, created = Comment.objects.update_or_create(
                article_id=article_id,
                user=request.user,
                defaults={'content': content}
            )
            action = 'create' if created else 'update'
            return JsonResponse({'success': True, 'action': action})
        else:
            return JsonResponse({'success': False, 'error': 'コメント内容がありません。'})
        
        
class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, article_id):
        comment = get_object_or_404(Comment, article_id=article_id, user=request.user)
        comment.delete()
        return JsonResponse({'success': True})
