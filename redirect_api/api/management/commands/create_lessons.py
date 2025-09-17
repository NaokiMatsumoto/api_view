from django.core.management.base import BaseCommand
from api.models import Lesson

class Command(BaseCommand):
    help = 'Create initial lesson data'

    def handle(self, *args, **options):
        lessons_data = [
            {'id': 'U01', 'title': 'Flask', 'url': 'https://www.udemy.com/course/flaskpythonweb/?couponCode=yyyymmdd_NM_FLASK'},
            {'id': 'U02', 'title': 'Linuxマスター', 'url': 'https://www.udemy.com/course/linuxlpic/?couponCode=yyyymmdd_NM_LINUX'},
            {'id': 'U03', 'title': 'ITパスポート', 'url': 'https://www.udemy.com/course/it-it-sf/?couponCode=yyyymmdd_NM_ITPASS'},
            {'id': 'U04', 'title': '基本情報', 'url': 'https://www.udemy.com/course/kihonjoho-oyojoho/?couponCode=yyyymmdd_NM_KIJO'},
            {'id': 'U05', 'title': 'Python', 'url': 'https://www.udemy.com/course/python-python/?couponCode=yyyymmdd_NM_PYTHON'},
            {'id': 'U06', 'title': 'デザインパターン', 'url': 'https://www.udemy.com/course/python-mx/?couponCode=yyyymmdd_NM_DESIGN'},
            {'id': 'U07', 'title': 'Django', 'url': 'https://www.udemy.com/course/python-django-web/?couponCode=yyyymmdd_NM_DJANGO'},
            {'id': 'U08', 'title': 'Shell', 'url': 'https://www.udemy.com/course/30awslinux/?couponCode=yyyymmdd_NM_A_LINUX'},
            {'id': 'U09', 'title': 'SQL', 'url': 'https://www.udemy.com/course/3sqlmysql/?couponCode=yyyymmdd_NM_SQL'},
            {'id': 'U10', 'title': 'Django Rest', 'url': 'https://www.udemy.com/course/django-restful-apigraphqlapi/?couponCode=yyyymmdd_NM_D_REST'},
            {'id': 'U11', 'title': '生成AI', 'url': 'https://www.udemy.com/course/2024-aichatgpt-github-copilot/?couponCode=yyyymmdd_NM_GPT'},
        ]

        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                id=lesson_data['id'],
                defaults={
                    'title': lesson_data['title'],
                    'url': lesson_data['url'],
                    'default_url': lesson_data['url']  # default_urlにも同じURLを設定
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created lesson: {lesson.title} ({lesson.id})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Lesson already exists: {lesson.title} ({lesson.id})')
                )