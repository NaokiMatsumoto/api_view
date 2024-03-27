from django.core.management.base import BaseCommand
from news.models import NewsSource, NewsArticle
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scrape_news():
    news_sources = NewsSource.objects.all()
    for news_source in news_sources:
        response = requests.get(news_source.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = soup.find_all('a', href=True)
        processed_urls = set()
        for link in article_links:
            article_url = link['href']
            article_title = link.text.strip()
            article_host = urlparse(article_url).hostname
            if not article_url:
                continue
            if article_url in processed_urls:  # 重複チェックを追加
                continue
            if article_host != news_source.host:
                continue
            processed_urls.add(article_url)
            
            if not NewsArticle.objects.filter(url=article_url).exists():
                NewsArticle.objects.create(
                    news_source=news_source,
                    title=article_title,
                    url=article_url,
                )


class Command(BaseCommand):
    help = 'Scrape news articles from registered sources'

    def handle(self, *args, **options):
        scrape_news()
        # self.stdout.write(self.style.SUCCESS('News articles scraped successfully'))
