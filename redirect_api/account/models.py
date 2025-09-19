from django.db import models
from django.core.exceptions import ValidationError


class ExternalIntegration(models.Model):
	class Provider(models.TextChoices):
		SLACK = "slack", "Slack"
		X = "x", "X (Twitter)"

	provider = models.CharField(max_length=20, choices=Provider.choices, db_index=True)
	name = models.CharField(max_length=100)
	is_active = models.BooleanField(default=True, db_index=True)
	config = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def clean(self):
		cfg = self.config or {}
		if self.provider == self.Provider.SLACK:
			if not cfg.get("webhook_url"):
				raise ValidationError("Slackは config.webhook_url が必須です。")
		elif self.provider == self.Provider.X:
			# Xの資格情報は環境変数で扱う想定。ここでは参照用のenv_prefixなどがあれば良い。
			if not cfg.get("env_prefix"):
				raise ValidationError("Xは config.env_prefix が必須です。")

	def __str__(self) -> str:
		return f"[{self.provider}] {self.name}"

	class Meta:
		indexes = [
			models.Index(fields=["provider", "is_active"]),
		]
		ordering = ["provider", "name"]
		db_table = "external_integration"
