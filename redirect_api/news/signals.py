from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsSource, NewsArticle
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_articles(news_source):
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
                shown=False
            )

@receiver(post_save, sender=NewsSource)
def do_something_after_insert(sender, instance, created, **kwargs):
    if created:
        # 新しいレコードが挿入された場合の処理をここに書く
        print(f"New NewsSource inserted: {instance.name}")
        # 必要な処理を追加する
        scrape_articles(instance)
