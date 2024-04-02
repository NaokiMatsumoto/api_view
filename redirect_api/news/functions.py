from .models import NewsSource, NewsArticle
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_articles(news_source, shown=True):
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
        if article_url in processed_urls:
            continue
        if article_host is None:
            article_url = f"https://{news_source.host}{article_url}"
        processed_urls.add(article_url)

        if NewsArticle.objects.filter(url=article_url).exists():
            continue

        NewsArticle.objects.create(
            news_source=news_source,
            title=article_title,
            url=article_url,
            shown=shown
        )

def scrape_all_news_sources():
    news_sources = NewsSource.objects.all()
    for news_source in news_sources:
        scrape_articles(news_source)