from __future__ import annotations

from datetime import date as _date
from typing import Optional

from django.db import models


class PersonalSeminar(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=50, choices=[("online", "オンライン"), ("offline", "オフライン")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def base_date(self) -> Optional[_date]:
        """PersonalSeminarDateの最も早い日付を基準日とする"""
        first_date = self.dates.order_by("date").first()  # type: ignore[attr-defined]
        return first_date.date if first_date else None

    def __str__(self) -> str:
        return self.title

    @property
    def total_tasks_count(self) -> int:
        return self.tasks.count()  # type: ignore[attr-defined]

    @property
    def completed_tasks_count(self) -> int:
        return self.tasks.filter(is_done=True).count()  # type: ignore[attr-defined]

    @property
    def completed_percent(self) -> int:
        total = self.total_tasks_count
        if total == 0:
            return 0
        return round(self.completed_tasks_count * 100 / total)

    @property
    def all_dates_past(self) -> bool:
        qs = self.dates.all()  # type: ignore[attr-defined]
        if not qs.exists():
            return False
        today = _date.today()
        return all(d.date < today for d in qs)

    @property
    def has_future_dates(self) -> bool:
        today = _date.today()
        return self.dates.filter(date__gte=today).exists()  # type: ignore[attr-defined]

    class Meta:
        db_table = "personal_seminar"


class PersonalSeminarDate(models.Model):
    seminar = models.ForeignKey(PersonalSeminar, related_name="dates", on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self) -> str:
        return f"{self.seminar.title} - {self.date}"

    @property
    def is_past(self) -> bool:
        return self.date < _date.today()

    class Meta:
        db_table = "personal_seminar_date"


class PreparationTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "preparation_template"


class PreparationTaskTemplate(models.Model):
    template = models.ForeignKey(PreparationTemplate, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    relative_days_before = models.IntegerField(null=True, blank=True)  # 開催日からの相対日
    default_assignee = models.CharField(max_length=100, blank=True)
    default_notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.template.name})"

    @property
    def when_display(self) -> str:
        """相対日を「N日前（W週間D日前）」または「N日前（W週間前）」形式で返す。
        例: -55日前（-7週間6日前）, -56日前（-8週間前）
        relative_days_before が未設定なら「未設定」。
        """
        n = self.relative_days_before
        if n is None:
            return "未設定"
        absn = abs(n)
        weeks = absn // 7
        days = absn % 7
        # 符号を保った表示
        if weeks > 0 and days > 0:
            w = -weeks if n < 0 else weeks
            d = -days if n < 0 else days
            return f"{n}日前（{w}週間{d}日前）"
        if weeks > 0 and days == 0:
            w = -weeks if n < 0 else weeks
            return f"{n}日前（{w}週間前）"
        # 週に満たない場合は日だけ
        return f"{n}日前"

    class Meta:
        db_table = "preparation_task_template"
        ordering = ["id"]


class PreparationTask(models.Model):
    seminar = models.ForeignKey(PersonalSeminar, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    deadline = models.DateField(db_index=True)
    assignee = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_done = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.deadline}"

    @property
    def is_overdue(self) -> bool:
        """未完了 かつ 期限超過かどうか"""
        from datetime import date as _date
        try:
            return (not self.is_done) and (self.deadline < _date.today())
        except Exception:
            return False

    class Meta:
        db_table = "preparation_task"


class Participant(models.Model):
    seminar = models.ForeignKey(PersonalSeminar, related_name="participants", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.seminar.title})"

    class Meta:
        db_table = "participant"


class NotificationSetting(models.Model):
    days_before = models.IntegerField(help_text="開催日の何日前に通知するか")
    integrations = models.ManyToManyField(
        'account.ExternalIntegration',
        related_name='notification_settings',
        blank=True,
        help_text="この通知設定で使用する外部連携（複数可。未指定時はアプリ共通設定を使用）",
    )

    def __str__(self):
        return f"{self.days_before}日前通知"

    class Meta:
        db_table = "notification_setting"
