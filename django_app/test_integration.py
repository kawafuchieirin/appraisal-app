#!/usr/bin/env python3
"""
Django-FastAPI統合テストスクリプト
"""

import requests
import time

def test_django_fastapi_integration():
    """
    Django -> FastAPI 統合テスト
    """
    print("🔗 Django-FastAPI統合テスト開始\n")
    
    # 1. Django フォームページアクセステスト
    print("=== 1. Django フォームページテスト ===")
    try:
        response = requests.get("http://localhost:8080/valuation/", timeout=5)
        if response.status_code == 200:
            print("✅ Django フォームページ正常表示")
            print(f"   ステータス: {response.status_code}")
            print(f"   ページサイズ: {len(response.content)} bytes")
            
            # CSRF トークン確認
            if 'csrfmiddlewaretoken' in response.text:
                print("✅ CSRFトークン確認")
            else:
                print("⚠️ CSRFトークンが見つかりません")
        else:
            print(f"❌ Django ページエラー: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Django接続エラー: {e}")
        return False
    
    # 2. FastAPI エンドポイント直接テスト
    print("\n=== 2. FastAPI エンドポイント直接テスト ===")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ FastAPI ヘルスチェック成功")
            print(f"   モデル読み込み: {data.get('model_loaded')}")
            print(f"   モデルタイプ: {data.get('model_info', {}).get('model_type')}")
        else:
            print(f"❌ FastAPI エラー: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FastAPI接続エラー: {e}")
        return False
    
    # 3. Django セッション経由でのAPI呼び出しテスト
    print("\n=== 3. Django セッション統合テスト ===")
    session = requests.Session()
    
    try:
        # まずDjangoフォームページを取得してCSRFトークンを取得
        form_response = session.get("http://localhost:8080/valuation/", timeout=5)
        
        if form_response.status_code == 200:
            # CSRFトークンを抽出
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form_response.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRFトークン取得: {csrf_token[:20]}...")
                
                # フォーム送信データ
                form_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'building_area': 80.0,
                    'land_area': 120.0,
                    'building_age': 10,
                    'ward_name': '世田谷区',
                    'year': 2024,
                    'quarter': 1
                }
                
                # フォーム送信
                result_response = session.post(
                    "http://localhost:8080/valuation/result/",
                    data=form_data,
                    timeout=10
                )
                
                if result_response.status_code == 200:
                    print("✅ Django経由査定成功")
                    print(f"   レスポンスサイズ: {len(result_response.content)} bytes")
                    
                    # 結果ページに価格情報があるかチェック
                    if '万円' in result_response.text:
                        price_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*万円', result_response.text)
                        if price_match:
                            price = price_match.group(1)
                            print(f"✅ 予測価格表示確認: {price}万円")
                        else:
                            print("⚠️ 価格表示パターンが見つかりません")
                    
                    if '信頼度' in result_response.text:
                        print("✅ 信頼度情報確認")
                    
                    return True
                else:
                    print(f"❌ Django フォーム送信エラー: {result_response.status_code}")
                    print(f"   レスポンス内容: {result_response.text[:500]}...")
                    return False
            else:
                print("❌ CSRFトークンが見つかりません")
                return False
        else:
            print(f"❌ Django フォーム取得エラー: {form_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Django統合テストエラー: {e}")
        return False

def main():
    """
    メイン実行
    """
    print("🧪 Django-FastAPI統合テスト\n")
    
    # サーバー起動確認
    print("サーバー起動確認中...")
    
    # Django サーバー確認
    try:
        response = requests.get("http://localhost:8080/", timeout=3)
        print("✅ Django サーバー (8080) 起動確認")
    except:
        print("❌ Django サーバーが起動していません (8080ポート)")
        print("次のコマンドで起動してください: python manage.py runserver 8080")
        return
    
    # FastAPI サーバー確認
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        print("✅ FastAPI サーバー (8000) 起動確認")
    except:
        print("❌ FastAPI サーバーが起動していません (8000ポート)")
        print("次のコマンドで起動してください: python main.py")
        return
    
    print("\n" + "="*50)
    
    # 統合テスト実行
    success = test_django_fastapi_integration()
    
    print("\n" + "="*50)
    print("🧪 統合テスト結果")
    print("="*50)
    
    if success:
        print("✅ 全ての統合テストが成功しました！")
        print("\n📋 確認済み項目:")
        print("   - Django フォーム表示")
        print("   - FastAPI API 接続")
        print("   - Django -> FastAPI データ送信")
        print("   - 査定結果表示")
        print("   - CSRF セキュリティ")
    else:
        print("❌ 一部の統合テストが失敗しました")
    
    print(f"\n🕒 テスト完了: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()