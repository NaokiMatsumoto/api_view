from .models import NewsSource, NewsArticle
import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def is_date_release_string(text):
    pattern = r'^\d{4}/\d{1,2}/\d{1,2} Release '
    return bool(re.match(pattern, text))

def scrape_articles(news_source, shown=True):
    response = requests.get(news_source.url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_links = soup.find_all('a', href=True)
    processed_urls = set()

    for link in article_links:
        article_url = link['href']
        article_title = link.text.strip()
        article_host = urlparse(article_url).hostname
        
        if not all([article_url, article_title]):
            continue
        if article_url in processed_urls:
            continue
        if article_host is not None and news_source.host != article_host:
            continue
        if article_host is None:
            article_url = f"https://{news_source.host}{article_url}"
        if article_host == 'ideasforgood.jp' and article_title.isdigit():
            continue
        if article_host == 'weetracker.com' and article_title.startswith("Contact"):
            continue
        if article_host == 'kr-asia.com' and article_title.find("[email protected]") != -1:
            continue
        if article_host == 'techable.jp' and is_date_release_string(article_title):
            continue
        
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