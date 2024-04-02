from django.views.generic import ListView, RedirectView
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .models import NewsSource, NewsArticle
from datetime import datetime, date
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from calendar import monthrange
from django.utils import timezone

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
        if adjusted_date is None:
            datetime_now = timezone.now()
            year, month, day = datetime_now.year, datetime_now.month, datetime_now.day
        else:
            year, month, day = adjusted_date
        
        self.published_at = datetime(year, month, day)
        queryset = super().get_queryset().prefetch_related(
            Prefetch(
                'newsarticle_set',
                queryset=NewsArticle.objects.filter(shown=True, published_at=self.published_at),
                to_attr='published_articles'
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.published_at is None:
            context['published_at'] = timezone.now().date()
        else:
            context['published_at'] = self.published_at
        return context


@require_POST
@login_required
def hide_articles(request, year, month, day):
    article_ids = request.POST.get('article_ids', '').split(',')
    NewsArticle.objects.filter(id__in=article_ids).update(shown=False)
    return redirect(reverse('news_list', kwargs={
        'year': year,
        'month': month,
        'day': day
    }))
