from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # デフォルトの例外ハンドラを呼び出します。
    response = exception_handler(exc, context)

    # 例外が404エラーの場合、カスタムレスポンスを生成します。
    if response is not None and response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = {
            'error': 'Not found',
            'message': 'このリソースは見つかりませんでした。'
        }

    return response
