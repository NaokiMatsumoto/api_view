from django.core.management.base import BaseCommand
from news.functions import scrape_all_news_sources



class Command(BaseCommand):
    help = 'Scrape news articles from registered sources'

    def handle(self, *args, **options):
        scrape_all_news_sources()
        # self.stdout.write(self.style.SUCCESS('News articles scraped successfully'))
