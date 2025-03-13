# Generated by Django 5.0.2 on 2025-03-12 05:17

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClaudeModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('model_id', models.CharField(max_length=100, unique=True, verbose_name='モデルID')),
                ('name', models.CharField(max_length=100, verbose_name='モデル名')),
                ('description', models.TextField(blank=True, verbose_name='説明')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'Claudeモデル',
                'verbose_name_plural': 'Claudeモデル',
            },
        ),
        migrations.CreateModel(
            name='XAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='アカウント名')),
                ('api_key', models.CharField(max_length=255, verbose_name='X API キー')),
                ('api_secret', models.CharField(max_length=255, verbose_name='X API シークレット')),
                ('access_token', models.CharField(max_length=255, verbose_name='アクセストークン')),
                ('access_token_secret', models.CharField(max_length=255, verbose_name='アクセストークンシークレット')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'Xアカウント',
                'verbose_name_plural': 'Xアカウント',
            },
        ),
        migrations.CreateModel(
            name='TweetPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='プロンプト名')),
                ('reference_text', models.TextField(default='', verbose_name='参照元となるテキスト')),
                ('draft_prompt', models.TextField(help_text='下書きを生成するためのプロンプト。{reference_text}は参照元テキストに置き換えられます。', verbose_name='下書きプロンプト')),
                ('refinement_prompt', models.TextField(help_text='下書きの出力を校正するためのプロンプト。{draft}は下書きの内容に置き換えられます。', verbose_name='校正プロンプト')),
                ('target_url', models.URLField(blank=True, verbose_name='遷移先URL')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('last_tweeted_at', models.DateTimeField(blank=True, null=True, verbose_name='最終投稿日時')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('draft_claude_model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='draft_prompts', to='twitter_bot.claudemodel', verbose_name='下書き生成用Claudeモデル')),
                ('refinement_claude_model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='refinement_prompts', to='twitter_bot.claudemodel', verbose_name='校正用Claudeモデル')),
            ],
            options={
                'verbose_name': 'ツイートプロンプト',
                'verbose_name_plural': 'ツイートプロンプト',
            },
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tweet_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='ツイートID')),
                ('content', models.TextField(verbose_name='ツイート内容')),
                ('status', models.CharField(choices=[('success', '成功'), ('failed', '失敗')], default='success', max_length=20, verbose_name='ステータス')),
                ('url', models.URLField(blank=True, verbose_name='ツイートURL')),
                ('posted_at', models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tweets', to='twitter_bot.tweetprompt', verbose_name='プロンプト')),
            ],
            options={
                'verbose_name': 'ツイート履歴',
                'verbose_name_plural': 'ツイート履歴',
                'ordering': ['-posted_at'],
            },
        ),
        migrations.CreateModel(
            name='TweetSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hour', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)], verbose_name='時')),
                ('minute', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(59)], verbose_name='分')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': 'ツイートスケジュール',
                'verbose_name_plural': 'ツイートスケジュール',
                'ordering': ['hour', 'minute'],
                'unique_together': {('hour', 'minute')},
            },
        ),
        migrations.AddField(
            model_name='tweetprompt',
            name='schedules',
            field=models.ManyToManyField(related_name='prompts', to='twitter_bot.tweetschedule', verbose_name='スケジュール'),
        ),
        migrations.AddField(
            model_name='tweetprompt',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prompts', to='twitter_bot.xaccount', verbose_name='Xアカウント'),
        ),
    ]
