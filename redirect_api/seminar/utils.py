from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.utils.dateparse import parse_date
from django.conf import settings

import json
import urllib.request
import urllib.error
import ssl
try:
    import certifi  # type: ignore
    _CERTIFI_CA = certifi.where()
except Exception:  # certifi 未インストール時はデフォルトCAを使用
    certifi = None  # type: ignore
    _CERTIFI_CA = None

from .models import PreparationTask

if TYPE_CHECKING:
    from .models import PreparationTemplate, PersonalSeminar as Seminar


WEEKDAYS: list[str] = ["月", "火", "水", "木", "金", "土", "日"]


def create_tasks_from_template(seminar: "Seminar", template: "PreparationTemplate") -> None:
    """Seminar作成時にPreparationTaskTemplateからPreparationTaskを生成"""
    base_date = seminar.base_date()
    if not base_date:
        return  # SeminarDateがない場合はスキップ

    for task_template in template.tasks.all():  # type: ignore[attr-defined]
        # 相対日のみを利用
        if task_template.relative_days_before is None:
            continue  # 日付がないタスクはスキップ

        deadline = base_date + timedelta(days=task_template.relative_days_before)
        PreparationTask.objects.create(
            seminar=seminar,
            name=task_template.name,
            deadline=deadline,
            assignee=task_template.default_assignee,
            notes=task_template.default_notes,
        )


def parse_date_input(value: str) -> Optional[date]:
    """POSTから受け取った日付文字列を安全にdateへ変換"""
    value = value.strip()
    if not value:
        return None

    parsed = parse_date(value)
    if parsed is not None:
        return parsed

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def describe_relative_days(target: date, reference: Optional[date] = None) -> str:
    today = reference or date.today()
    if target == today:
        return "本日"

    delta_days = (target - today).days
    if delta_days > 0:
        return f"{delta_days}日後"
    return f"{abs(delta_days)}日前"


def format_date_with_weekday(target: date) -> str:
    weekday_index = target.weekday()
    weekday = WEEKDAYS[weekday_index] if 0 <= weekday_index < len(WEEKDAYS) else ""
    return f"{target.strftime('%Y/%m/%d')} ({weekday})"


def serialize_task(task: PreparationTask) -> Dict[str, Any]:
    deadline = task.deadline
    return {
        "pk": task.pk,
        "name": task.name,
        "is_done": task.is_done,
        "deadline_iso": deadline.isoformat(),
        "deadline_display": format_date_with_weekday(deadline),
        "date_key": deadline.isoformat(),
        "relative_text": describe_relative_days(deadline),
        "is_overdue": task.is_overdue,
    }


def post_to_slack(text: str, *, webhook_url: Optional[str] = None, blocks: Optional[list[dict]] = None) -> bool:
    """Slack Incoming Webhook に投稿。失敗しても例外を外に投げず False を返す。
    依存を最小化するため標準ライブラリで送信。
    """
    url = webhook_url or getattr(settings, 'SLACK_TASK_WEBHOOK_URL', None)
    if not url:
        return False

    payload: Dict[str, Any] = {"text": text}
    if blocks:
        payload["blocks"] = blocks
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        # certifi があればその CA バンドルを使用
        context = ssl.create_default_context(cafile=_CERTIFI_CA) if _CERTIFI_CA else ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(e)
        return False
