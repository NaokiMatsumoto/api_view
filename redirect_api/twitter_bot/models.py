
from django.db import models
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class XAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="アカウント名")
    api_key = models.CharField(max_length=255, verbose_name="X API キー")
    api_secret = models.CharField(max_length=255, verbose_name="X API シークレット")
    access_token = models.CharField(max_length=255, verbose_name="アクセストークン")
    access_token_secret = models.CharField(max_length=255, verbose_name="アクセストークンシークレット")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Xアカウント"
        verbose_name_plural = "Xアカウント"



class ClaudeModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_id = models.CharField(max_length=100, unique=True, verbose_name="モデルID")
    name = models.CharField(max_length=100, verbose_name="モデル名")
    description = models.TextField(blank=True, verbose_name="説明")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Claudeモデル"
        verbose_name_plural = "Claudeモデル"

class TweetSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hour = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(23)], verbose_name="時")
    minute = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(59)], verbose_name="分")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    def __str__(self):
        return f"{self.hour:02d}:{self.minute:02d}"
    
    class Meta:
        verbose_name = "ツイートスケジュール"
        verbose_name_plural = "ツイートスケジュール"
        ordering = ['hour', 'minute']
        unique_together = ['hour', 'minute']

class TweetPrompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(XAccount, on_delete=models.CASCADE, related_name='prompts', verbose_name="Xアカウント")
    name = models.CharField(max_length=100, verbose_name="プロンプト名")
    reference_text = models.TextField(verbose_name="参照元となるテキスト", default='')
    draft_prompt = models.TextField(verbose_name="下書きプロンプト", 
                                help_text="下書きを生成するためのプロンプト。{reference_text}は参照元テキストに置き換えられます。")
    draft_claude_model = models.ForeignKey(
        ClaudeModel, 
        on_delete=models.PROTECT, 
        related_name='draft_prompts', 
        verbose_name="下書き生成用Claudeモデル"
    )
    refinement_prompt = models.TextField(verbose_name="校正プロンプト",
                                    help_text="下書きの出力を校正するためのプロンプト。{draft}は下書きの内容に置き換えられます。")
    refinement_claude_model = models.ForeignKey(
        ClaudeModel, 
        on_delete=models.PROTECT, 
        related_name='refinement_prompts', 
        verbose_name="校正用Claudeモデル"
    )
    target_url = models.TextField(verbose_name="遷移先URL", blank=True)
    schedules = models.ManyToManyField(TweetSchedule, related_name='prompts', verbose_name="スケジュール")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    last_tweeted_at = models.DateTimeField(null=True, blank=True, verbose_name="最終投稿日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    def clean(self):
        # draft_promptに{reference_text}が含まれているか確認
        if '{reference_text}' not in self.draft_prompt:
            raise ValidationError({
                'draft_prompt': '下書きプロンプトには"{reference_text}"が含まれている必要があります。'
            })
        
        # refinement_promptに{draft}が含まれているか確認
        if '{draft}' not in self.refinement_prompt:
            raise ValidationError({
                'refinement_prompt': '校正プロンプトには"{draft}"が含まれている必要があります。'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.account.name})"
    
    class Meta:
        verbose_name = "ツイートプロンプト"
        verbose_name_plural = "ツイートプロンプト"


class Tweet(models.Model):
    """投稿されたツイートの記録"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.ForeignKey('TweetPrompt', on_delete=models.CASCADE, related_name='tweets', verbose_name="プロンプト")
    tweet_id = models.CharField(max_length=255, verbose_name="ツイートID", blank=True, null=True)
    content = models.TextField(verbose_name="ツイート内容")
    status = models.CharField(max_length=20, verbose_name="ステータス", 
                             choices=[
                                 ('success', '成功'),
                                 ('failed', '失敗')
                             ], default='success')
    url = models.URLField(verbose_name="ツイートURL", blank=True)
    posted_at = models.DateTimeField(verbose_name="投稿日時", auto_now_add=True)
    
    def __str__(self):
        return f"{self.prompt.name} - {self.posted_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_tweet_url(self):
        if self.tweet_id and self.status == 'success':
            return f"https://x.com/{self.prompt.account.name}/status/{self.tweet_id}"
        return ""
    
    def tweet_link(self):
        url = self.get_tweet_url()
        if url:
            return format_html('<a href="{}" target="_blank">Xで表示</a>', url)
        return "リンクなし"
    tweet_link.short_description = "ツイートリンク"
    
    class Meta:
        verbose_name = "ツイート履歴"
        verbose_name_plural = "ツイート履歴"
        ordering = ['-posted_at']
