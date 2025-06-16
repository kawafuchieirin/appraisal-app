import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import EstimateForm

def index(request):
    """
    査定フォーム表示
    """
    form = EstimateForm()
    return render(request, 'valuation/index.html', {'form': form})

def result(request):
    """
    査定結果表示（環境変数による切り替え対応）
    """
    if request.method == 'POST':
        form = EstimateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # 🔧 API利用可能性チェック
            if not settings.USE_MODEL_API:
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'input_data': data,
                    'error': '現在、査定APIは利用できません。しばらくしてから再度お試しください。',
                    'error_type': 'api_disabled'
                })
            
            # 🌐 FastAPI呼び出し
            api_url = f"{settings.FASTAPI_URL}/predict"
            
            try:
                response = requests.post(
                    api_url, 
                    json=data, 
                    timeout=settings.FASTAPI_TIMEOUT
                )
                response.raise_for_status()
                result = response.json()
                
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'result': result,
                    'input_data': data
                })
                
            except requests.exceptions.ConnectionError:
                error_msg = "査定APIに接続できません。しばらくしてから再度お試しください。"
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'input_data': data,
                    'error': error_msg,
                    'error_type': 'connection_error'
                })
                
            except requests.exceptions.Timeout:
                error_msg = "査定処理がタイムアウトしました。しばらく時間をおいて再試行してください。"
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'input_data': data,
                    'error': error_msg,
                    'error_type': 'timeout'
                })
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    error_msg = "査定サービスが一時的に利用できません。しばらくしてから再度お試しください。"
                elif e.response.status_code == 422:
                    error_msg = "入力データに問題があります。入力内容を確認してください。"
                else:
                    error_msg = "査定処理でエラーが発生しました。しばらくしてから再度お試しください。"
                
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'input_data': data,
                    'error': error_msg,
                    'error_type': 'http_error'
                })
                
            except Exception as e:
                error_msg = "予期しないエラーが発生しました。しばらくしてから再度お試しください。"
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'input_data': data,
                    'error': error_msg,
                    'error_type': 'unexpected_error'
                })
        else:
            # フォームバリデーションエラー
            messages.error(request, "入力内容に誤りがあります。確認してください。")
    else:
        form = EstimateForm()
    
    return render(request, 'valuation/index.html', {'form': form})
