from django.core.management.base import BaseCommand
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from django.conf import settings
from twitter_bot.models import TweetSchedule, TweetPrompt, Tweet, XAccount
import pytz
import os



class Command(BaseCommand):
    help = 'スケジュールされたツイートの下書きを生成し、洗練するコマンド'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='名前を指定')
        parser.add_argument('--hour', type=str, help='特定の時間を指定（デフォルトは現在時刻）')

    def handle(self, *args, **options):
        try:
            # 現在の時間または指定された時間を取得
            specified_hour = options.get('hour')
            now_hour = specified_hour if specified_hour else self.get_current_hour()
            
            # アクティブなスケジュールを取得
            schedules = self.get_active_schedules(now_hour)
            if not schedules.exists():
                self.stdout.write(self.style.WARNING(f"時間 {now_hour}時 のアクティブなスケジュールは見つかりませんでした。"))
                return
            
            # プロンプトを処理
            self.process_prompts(schedules)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"エラーが発生しました: {str(e)}"))
    
    def get_current_hour(self):
        """現在の時間（時）を返す"""
        return datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H')
    
    def get_active_schedules(self, hour):
        """指定された時間のアクティブなスケジュールを取得"""
        return TweetSchedule.objects.filter(
            hour=hour,
            is_active=True
        )
    
    def get_anthropic_api_key(self):
        """Anthropic APIキーを取得"""
        # 設定ファイルや環境変数からAPIキーを取得
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None) or os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic APIキーが設定されていません")
        return api_key
    
    def create_llm_instance(self, model_id):
        """指定されたモデルIDでLLMインスタンスを作成"""
        api_key = self.get_anthropic_api_key()
        return ChatAnthropic(
            model=model_id,
            api_key=api_key,
        )
    
    def generate_text(self, prompt_template, llm, input_variables):
        """プロンプトとLLMを使用してテキストを生成"""
        chain = prompt_template | llm | StrOutputParser()
        return chain.invoke(input_variables)
    
    def process_prompts(self, schedules):
        """スケジュールに関連するプロンプトを処理"""
        prompts = TweetPrompt.objects.filter(
            schedules__in=schedules,
            is_active=True
        ).distinct().all()
        
        prompt_count = prompts.count()
        self.stdout.write(f"処理するプロンプト数: {prompt_count}")
        
        for index, prompt in enumerate(prompts, 1):
            self.stdout.write(f"プロンプト {index}/{prompt_count} を処理中...")
            try:
                self.process_single_prompt(prompt)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"プロンプト処理エラー: {str(e)}"))
    
    def process_single_prompt(self, prompt):
        """単一のプロンプトを処理"""
        # 下書き生成
        self.stdout.write(f"下書きモデル: {prompt.draft_claude_model.model_id} を使用中")
        draft_prompt_template = ChatPromptTemplate.from_template(prompt.draft_prompt)
        draft_llm = self.create_llm_instance(prompt.draft_claude_model.model_id)
        
        draft_text = self.generate_text(
            draft_prompt_template, 
            draft_llm, 
            {"reference_text": prompt.reference_text}
        )
        self.stdout.write("下書きを生成しました")
        self.stdout.write(f"下書き: {draft_text}")
        
        # 洗練処理
        self.stdout.write(f"洗練モデル: {prompt.refinement_claude_model.model_id} を使用中")
        refinement_prompt_template = ChatPromptTemplate.from_template(prompt.refinement_prompt)
        refinement_llm = self.create_llm_instance(prompt.refinement_claude_model.model_id)
        
        refinement_text = self.generate_text(
            refinement_prompt_template,
            refinement_llm,
            {"draft": draft_text}
        )
        self.stdout.write("洗練テキストを生成しました")
        
        # ここで生成されたテキストを保存したり、ツイートしたりする処理を追加できます
        self.save_tweet(prompt, refinement_text)
        ### ツイート
        tweet_content = refinement_text
        if prompt.target_url:
            tweet_content = f"{tweet_content}\nURL: {prompt.target_url}"
        self.post_to_twitter(tweet_content, prompt.account)
        # 結果の表示
        self.stdout.write(self.style.SUCCESS("処理完了"))
        self.stdout.write("生成されたテキスト:")
        self.stdout.write(refinement_text)
        
    def save_tweet(self, prompt, content):
        """生成されたテキストをTweetモデルに保存"""
        try:
            # ツイートの作成
            tweet = Tweet(
                prompt=prompt,
                content=content,
                status='success'  # デフォルトステータスは成功
            )
            tweet.save()
            self.stdout.write(f"ツイートをデータベースに保存しました（ID: {tweet.id}）")
            return tweet
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ツイートの保存中にエラーが発生しました: {str(e)}"))
            # エラーが発生した場合は失敗ステータスのレコードを作成
            try:
                failed_tweet = Tweet.objects.create(
                    prompt=prompt,
                    content=content,
                    status='failed'
                )
                self.stdout.write(f"失敗ステータスでツイートを記録しました（ID: {failed_tweet.id}）")
                return failed_tweet
            except Exception as inner_e:
                self.stdout.write(self.style.ERROR(f"失敗ステータスの記録中にエラーが発生しました: {str(inner_e)}"))
                return None
            
    def post_to_twitter(self, tweet_content: str, account: XAccount):
        """X(Twitter)にツイートを投稿する"""
        try:
            self.stdout.write(f"アカウント {account.name} でXに投稿しています...")
            
            # Twitter API v2を使用してツイートを投稿
            import tweepy
            
            # API資格情報を取得
            api_key = account.api_key
            api_secret = account.api_secret
            access_token = account.access_token
            access_token_secret = account.access_token_secret
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                self.stdout.write(self.style.ERROR("Twitter API資格情報が不足しています"))
                return None
            
            # Tweepyクライアントを初期化
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            # ツイートを投稿
            response = client.create_tweet(text=tweet_content)
            
            # レスポンスからツイートIDを取得
            if response.data and 'id' in response.data:
                return response.data
            
            return None
        
        except tweepy.TweepyException as e:
    # エラーの詳細情報を表示
            self.stdout.write(self.style.ERROR(f"Tweepy エラー: {str(e)}"))
            if hasattr(e, 'response') and e.response is not None:
                self.stdout.write(self.style.ERROR(f"ステータスコード: {e.response.status_code}"))
                self.stdout.write(self.style.ERROR(f"レスポンス内容: {e.response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"その他のエラー: {str(e)}"))
