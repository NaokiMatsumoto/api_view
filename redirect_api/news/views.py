from django.views.generic import ListView, RedirectView
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from .models import NewsSource, NewsArticle
from datetime import datetime, date
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


class NewsSourceListRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        today = date.today()
        return reverse('news_list', kwargs={
            'year': today.year,
            'month': today.month,
            'day': today.day
        })

class NewsSourceListView(ListView):
    model = NewsSource
    template_name = 'news_list.html'
    context_object_name = 'news_sources'

    def get_queryset(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        published_at = datetime(int(year), int(month), int(day))
        queryset = super().get_queryset().prefetch_related(
            Prefetch(
                'newsarticle_set',
                queryset=NewsArticle.objects.filter(shown=True, published_at=published_at),
                to_attr='published_articles'
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['published_at'] = datetime(
            int(self.kwargs['year']),
            int(self.kwargs['month']),
            int(self.kwargs['day'])
        )
        return context


@require_POST
def hide_articles(request, year, month, day):
    article_ids = request.POST.get('article_ids', '').split(',')
    NewsArticle.objects.filter(id__in=article_ids).update(shown=False)
    return redirect(reverse('news_list', kwargs={
        'year': year,
        'month': month,
        'day': day
    }))