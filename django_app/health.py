"""
Lambda Web Adapter用ヘルスチェックエンドポイント
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    """
    Lambda Web Adapter用のヘルスチェックエンドポイント
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'django-ui',
        'version': '1.0.0'
    })