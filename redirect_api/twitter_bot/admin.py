
from django.contrib import admin
from django import forms
from .models import (
    XAccount, ClaudeModel, TweetPrompt, TweetSchedule, Tweet
)


@admin.register(XAccount)
class XAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'prompt_count')
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active')
        }),
        ('API情報', {
            'fields': ('api_key', 'api_secret', 'access_token', 'access_token_secret'),
            'classes': ('collapse',),
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'プロンプト数'

@admin.register(ClaudeModel)
class ClaudeModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'is_active')
    search_fields = ('name', 'model_id')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'model_id', 'description', 'is_active')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    
 
@admin.register(TweetSchedule)
class TweetScheduleAdmin(admin.ModelAdmin):
    list_display = ('time_display', 'is_active', 'prompt_count')
    list_filter = ('is_active', 'hour')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('hour', 'minute', 'is_active')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def time_display(self, obj):
        return f"{obj.hour:02d}:{obj.minute:02d}"
    time_display.short_description = '時刻'
    
    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'プロンプト数'

@admin.register(TweetPrompt)
class TweetPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'draft_claude_model', 'refinement_claude_model', 'is_active', 'last_tweeted_at', 'schedule_display')
    list_filter = ('is_active', 'draft_claude_model', 'refinement_claude_model', 'account', 'schedules')
    search_fields = ('name',)
    autocomplete_fields = ['account', 'draft_claude_model', 'refinement_claude_model']
    readonly_fields = ('last_tweeted_at', 'created_at', 'updated_at')
    filter_horizontal = ('schedules',)  # ManyToManyフィールド用の水平選択ウィジェット
    
    fieldsets = (
        (None, {
            'fields': ('name', 'account', 'is_active')
        }),
        ('スケジュール設定', {
            'fields': ('schedules',),
            'description': '投稿するスケジュールを選択してください。複数選択可能です。'
        }),
        ('プロンプト設定', {
            'fields': ('reference_text',),
        }),
        ('下書き設定', {
            'fields': ('draft_prompt', 'draft_claude_model'),
            'description': '下書きプロンプトには必ず "{reference_text}" を含めてください。'
        }),
        ('校正設定', {
            'fields': ('refinement_prompt', 'refinement_claude_model', 'target_url'),
            'description': '校正プロンプトには必ず "{draft}" を含めてください。'
        }),
        ('システム情報', {
            'fields': ('last_tweeted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    actions = ['test_tweet']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'draft_prompt':
            field.widget = forms.Textarea(attrs={'rows': 10, 'placeholder': '下書きプロンプト (必ず{reference_text}を含めてください)'})
        if db_field.name == 'refinement_prompt':
            field.widget = forms.Textarea(attrs={'rows': 10, 'placeholder': '校正プロンプト (必ず{draft}を含めてください)'})
        return field
    
    def schedule_display(self, obj):
        """スケジュール情報を表示するためのメソッド"""
        schedules = obj.schedules.all().order_by('hour', 'minute')
        if not schedules:
            return "未設定"
        
        # 最大3つまで表示し、それ以上は省略
        schedule_list = [f"{s.hour:02d}:{s.minute:02d}" for s in schedules[:3]]
        if schedules.count() > 3:
            schedule_list.append(f"他 {schedules.count() - 3}件")
        
        return ", ".join(schedule_list)
    schedule_display.short_description = 'スケジュール'
    
    def get_queryset(self, request):
        """一覧表示時にschedules情報をプリフェッチして効率化"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('schedules')

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('prompt_name', 'account_name', 'short_content', 'status', 'tweet_link', 'posted_at')
    list_filter = ('status', 'prompt__account', 'posted_at')
    search_fields = ('content', 'prompt__name')
    readonly_fields = ('prompt', 'tweet_id', 'content', 'status', 'tweet_link', 'posted_at')
    fieldsets = (
        (None, {
            'fields': ('prompt', 'status', 'posted_at', 'tweet_link')
        }),
        ('ツイート内容', {
            'fields': ('content',),
        }),
        ('詳細情報', {
            'fields': ('tweet_id',),
            'classes': ('collapse',),
        }),
    )
    
    def short_content(self, obj):
        """ツイート内容の一部を表示（最初の50文字）"""
        if len(obj.content) > 50:
            return obj.content[:50] + "..."
        return obj.content
    short_content.short_description = "ツイート内容"
    
    def prompt_name(self, obj):
        return obj.prompt.name
    prompt_name.short_description = "プロンプト"
    
    def account_name(self, obj):
        return obj.prompt.account.name
    account_name.short_description = "アカウント"
    
    def has_add_permission(self, request):
        """ツイート履歴は手動で追加できないようにする"""
        return False