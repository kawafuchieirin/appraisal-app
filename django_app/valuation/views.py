import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EstimateForm

API_URL = "http://localhost:8000/predict"

def index(request):
    """
    査定フォーム表示
    """
    form = EstimateForm()
    return render(request, 'valuation/index.html', {'form': form})

def result(request):
    """
    査定結果表示
    """
    if request.method == 'POST':
        form = EstimateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            try:
                response = requests.post(API_URL, json=data, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                return render(request, 'valuation/result.html', {
                    'form': form,
                    'result': result,
                    'input_data': data
                })
                
            except requests.exceptions.ConnectionError:
                messages.error(request, "査定APIに接続できません。サーバーが起動していることを確認してください。")
            except requests.exceptions.Timeout:
                messages.error(request, "査定処理がタイムアウトしました。しばらく時間をおいて再試行してください。")
            except requests.exceptions.HTTPError as e:
                messages.error(request, f"査定処理でエラーが発生しました: {e}")
            except Exception as e:
                messages.error(request, f"予期しないエラーが発生しました: {e}")
        else:
            messages.error(request, "入力内容に誤りがあります。確認してください。")
    else:
        form = EstimateForm()
    
    return render(request, 'valuation/index.html', {'form': form})
