from __future__ import annotations

from collections import defaultdict
from datetime import date as _date, timedelta
from typing import Dict, List, Optional, Sequence, Set, Tuple

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import NotificationSetting, PreparationTask
from ...utils import post_to_slack
from django.conf import settings
from account.models import ExternalIntegration


class Command(BaseCommand):
    help = "未完了タスクの締切が N 日後のものを Slack に通知する (N は NotificationSetting で定義)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            dest="base_date",
            help="基準日(YYYY-MM-DD)。未指定時はローカル日付",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="送信せずに対象のみ表示",
        )
        parser.add_argument(
            "--webhook",
            dest="webhook_url",
            help="Slack Webhook URL (settings を上書き)",
        )

    def handle(self, *args, **options):
        """メイン処理。引数解釈→対象日抽出→日毎にタスク抽出→通知送信。

        挙動は従来と同一。可読性のためにヘルパー関数へ分割。
        """
        # 引数がなければ実行時のローカル日付を使用
        base_date = self._parse_date(options.get("base_date")) or timezone.localdate()

        # 実行時コンテキスト（引数が多くならないようインスタンスに保持）
        self._dry_run = bool(options.get("dry_run", False))
        self._override_webhook = options.get("webhook_url")
        self._sent_guard: Set[Tuple[str, int, int]] = set()  # (url, seminar_id, n)

        settings_qs = NotificationSetting.objects.prefetch_related("integrations").all()
        days_list: List[int] = self._collect_days(settings_qs)
        if not days_list:
            self.stdout.write(self.style.WARNING("NotificationSetting がありません。処理を終了します。"))
            return

        self.stdout.write(
            f"[send_task_notifications] base_date={base_date} days={days_list} dry_run={self._dry_run}"
        )

        total_to_notify = 0

        for n in days_list:
            target_date = base_date + timedelta(days=int(n))
            tasks = self._get_tasks_for_day(target_date)
            if not tasks:
                continue

            total_to_notify += len(tasks)
            grouped = self._group_tasks_by_seminar(tasks)

            for ns in settings_qs.filter(days_before=n):
                webhooks = self._resolve_webhooks(ns)
                if not webhooks:
                    self._warn(f"Webhook未設定のためスキップ: NotificationSetting id={ns.pk}")
                    continue

                for seminar_id, items in grouped.items():
                    text = self._build_message(items[0].seminar.title, n, target_date, items)
                    self._send(text, webhooks, ns_id=ns.pk, seminar_id=seminar_id, n=int(n))

        if total_to_notify == 0:
            self.stdout.write("対象タスクはありませんでした。")
        else:
            self.stdout.write(self.style.SUCCESS(f"合計 {total_to_notify} 件のタスク対象を処理しました。"))

    def _parse_date(self, s: Optional[str]) -> Optional[_date]:
        if not s:
            return None
        try:
            y, m, d = map(int, s.split("-"))
            return _date(y, m, d)
        except Exception:
            return None

    def _collect_days(self, settings_qs) -> List[int]:
        """NotificationSetting から通知日数(days_before)のユニーク集合を昇順で取得"""
        days: List[int] = sorted(set(settings_qs.values_list("days_before", flat=True)))
        return [int(x) for x in days]

    def _get_tasks_for_day(self, target_date: _date) -> List[PreparationTask]:
        """指定日の締切タスク(未完了)を取得。セミナーを select_related 済みで返す"""
        qs = (
            PreparationTask.objects.select_related("seminar")
            .filter(is_done=False, deadline=target_date)
            .order_by("seminar_id", "id")
        )
        return list(qs)

    def _group_tasks_by_seminar(self, tasks: Sequence[PreparationTask]) -> Dict[int, List[PreparationTask]]:
        grouped: Dict[int, List[PreparationTask]] = defaultdict(list)
        for t in tasks:
            grouped[t.seminar.pk].append(t)
        return grouped

    def _resolve_webhooks(self, ns: NotificationSetting) -> List[str]:
        """送信先Webhook一覧を解決。

        優先順位: コマンド引数(単一) > ns.integrations(複数Slack) > settingsフォールバック(単一)
        重複URLは除去。
        """
        if self._override_webhook:
            return [self._override_webhook]

        webhooks: List[str] = []
        for integ in ns.integrations.all():
            if integ.provider == ExternalIntegration.Provider.SLACK and integ.is_active:
                url = (integ.config or {}).get("webhook_url")
                if url:
                    webhooks.append(url)

        if not webhooks:
            fallback = getattr(settings, "SLACK_TASK_WEBHOOK_URL", None)
            if fallback:
                webhooks = [fallback]

        # 重複排除し順序維持
        return list(dict.fromkeys(webhooks))

    def _build_message(self, seminar_title: str, n: int, target_date: _date, items: Sequence[PreparationTask]) -> str:
        header = f"【タスク通知】締切まで{n}日: セミナー『{seminar_title}』 {target_date.isoformat()}"
        lines = [self._format_task_line(t) for t in items]
        return header + "\n" + "\n".join(lines)

    def _format_task_line(self, t: PreparationTask) -> str:
        assignee = (t.assignee or "未設定")
        return f"・{t.name}（担当: {assignee}）"

    def _send(
        self,
        text: str,
        webhooks: Sequence[str],
        *,
        ns_id: int,
        seminar_id: int,
        n: int,
    ) -> None:
        for url in webhooks:
            print(url)
            key = (url, seminar_id, n)
            if key in self._sent_guard:
                continue

            if self._dry_run:
                self.stdout.write("--- DRY RUN ---")
                self.stdout.write(f"to: {url}")
                self.stdout.write(text)
                ok = True
            else:
                ok = bool(post_to_slack(text, webhook_url=url))

            if ok:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"通知済: ns_id={ns_id} seminar_id={seminar_id} items={text.count('・')} n={n}"
                    )
                )
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f"Slack送信失敗: ns_id={ns_id} seminar_id={seminar_id} n={n}"
                    )
                )

            self._sent_guard.add(key)

    def _warn(self, msg: str) -> None:
        self.stderr.write(self.style.WARNING(msg))
