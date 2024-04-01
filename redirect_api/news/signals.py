from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NewsSource
from .functions import scrape_articles


@receiver(post_save, sender=NewsSource)
def do_something_after_insert(sender, instance, created, **kwargs):
    if created:
        # 必要な処理を追加する
        scrape_articles(news_source=instance, shown=False)
