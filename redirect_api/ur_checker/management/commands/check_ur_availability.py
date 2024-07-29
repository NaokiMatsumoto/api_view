from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Check UR apartment availability and send Slack notification'

    def handle(self, *args, **options):
        search_url = "https://chintai.r6.ur-net.go.jp/chintai/api/bukken/search/bukken_main/"
        form_data = {
            "rent_low": "",
            "rent_high": "",
            "floorspace_low": "",
            "floorspace_high": "",
            "shisya": "80",
            "danchi": "042",
            "shikibetu": "0",
            "newBukkenRoom": "",
            "orderByField": "0",
            "orderBySort": "0",
            "pageIndex": "0",
            "sp": "sp"
        }

        availability, count = self.check_apartment_availability(search_url, form_data)
        self.stdout.write(f"利用可能な部屋がありますか？ {availability}")
        self.stdout.write(f"利用可能な部屋の数: {count}")

        if availability:
            slack_webhook_url = settings.SLACK_WEBHOOK_URL
            if slack_webhook_url:
                message = f"*重要*: UR賃貸住宅に空きが出ました！\n利用可能な部屋の数: {count}"
                self.send_slack_notification(slack_webhook_url, message)
            else:
                self.stdout.write(self.style.WARNING("Slack Webhook URLが設定されていません。"))

    def check_apartment_availability(self, search_url, form_data):
        try:
            response = requests.post(search_url, data=form_data)
            response.raise_for_status()
            data = response.json()
            count = data.get('count', 0)
            return count > 0, count
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"リクエストエラーが発生しました: {e}"))
            return False, 0
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("JSONのパースに失敗しました。"))
            return False, 0
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"予期せぬエラーが発生しました: {e}"))
            return False, 0

    def send_slack_notification(self, webhook_url, message):
        payload = {
            "text": f"<@U07E2T4E1U7> {message}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<@U07E2T4E1U7> {message}",
                    }
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "X-Slack-Priority": "high"
        }
        response = requests.post(webhook_url, json=payload, headers=headers)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Slackへの通知送信に失敗しました。ステータスコード: {response.status_code}"))
        else:
            self.stdout.write(self.style.SUCCESS("Slackへの通知を送信しました。"))
