from django.core.management.base import BaseCommand
from seminar.models import PreparationTemplate, PreparationTaskTemplate


class Command(BaseCommand):
    help = "セミナー準備の標準テンプレートを投入する"

    def handle(self, *args, **options):
        template, created = PreparationTemplate.objects.get_or_create(
            name="標準セミナーテンプレート",
            defaults={"description": "セミナー開催用の基本準備タスクセット"}
        )

        if not created:
            self.stdout.write(self.style.WARNING("既にテンプレートが存在します"))
            return

        tasks = [
            # (相対日数, タスク名)
            (-56, "セミナー概要を決定（日時・場所・定員・料金）"),
            (-56, "会議室予約"),
            (-56, "ランディングページ（LP）を作成"),
            (-56, "connpass / Peatix にイベントページを公開"),
            (-56, "SNS用告知素材（画像・バナー）の作成開始"),

            (-49, "SNSで『告知開始』投稿（自己紹介＋セミナー告知）"),
            (-49, "広告を小額テスト配信（1日1,000円〜）"),

            (-42, "SNSで学習Tips投稿をスタート（毎日1本）"),
            (-42, "知人・過去受講者に直接案内（DM・メール）"),

            (-35, "connpassにイベント情報掲載"),
            (-35, "SNSで『セミナーの流れ』『講師実績（10万人受講）』を発信"),
            (-35, "広告クリエイティブ（テキスト・画像）を差し替えテスト"),

            (-28, "早割キャンペーンを開始（例：2週間前まで8,000円）"),
            (-28, "SNSで『早割スタート！残席カウント』投稿"),
            (-28, "広告予算を少し増額（2,000円/日）"),

            (-21, "SNSで『受講するとこんなスキルが得られる』具体例を紹介"),
            
            (-14, "『早割終了まであと○日』告知"),
            (-14, "広告を本格投入（3,000円/日）"),
            (-14, "SNSで『参加者の声』や『FAQ（初心者でも大丈夫？など）』を投稿"),

            (-7, "『残り○席です！』告知（SNS・メール）"),
            (-7, "広告クリエイティブを『残席僅少』版に切り替え"),
            (-7, "connpass参加者にリマインドメッセージ"),
            (-7, "資料作成完了"),

            (-5, "SNSで『あと○日で開催！』カウントダウン"),
            (-5, "参加者全員に案内メール（Zoomリンク／会場アクセス／持ち物など）"),

            (-1, "SNSで『いよいよ明日！』告知"),
            (-1, "受付リスト・資料を最終チェック"),
        ]

        for days, name in tasks:
            PreparationTaskTemplate.objects.create(
                template=template,
                name=name,
                relative_days_before=days,
            )

        self.stdout.write(self.style.SUCCESS("標準テンプレートを作成しました！"))
