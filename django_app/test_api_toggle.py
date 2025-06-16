#!/usr/bin/env python3
"""
API切り替え機能テストスクリプト
"""

import requests
import time
import os
from pathlib import Path

def test_api_enabled():
    """
    API有効時のテスト
    """
    print("=== API有効時テスト ===")
    
    # 環境変数をAPI有効に設定
    env_path = Path("django_app/.env")
    with open(env_path, "w") as f:
        f.write("USE_MODEL_API=true\n")
        f.write("FASTAPI_URL=http://localhost:8000\n")
        f.write("FASTAPI_TIMEOUT=10\n")
    
    print("✅ .env設定: USE_MODEL_API=true")
    
    # Django再起動を促す
    print("⚠️ Django サーバーを再起動してください")
    input("再起動後、Enterキーを押してください...")
    
    # テスト実行
    session = requests.Session()
    
    try:
        # フォーム取得
        form_response = session.get("http://localhost:8080/valuation/", timeout=5)
        
        if form_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form_response.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                
                # フォーム送信
                form_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'building_area': 80.0,
                    'land_area': 120.0,
                    'building_age': 10,
                    'ward_name': '世田谷区',
                    'year': 2024,
                    'quarter': 1
                }
                
                result_response = session.post(
                    "http://localhost:8080/valuation/result/",
                    data=form_data,
                    timeout=15
                )
                
                if result_response.status_code == 200:
                    if '万円' in result_response.text and 'エラー' not in result_response.text:
                        print("✅ API有効時: 正常に査定結果表示")
                        return True
                    else:
                        print("❌ API有効時: 査定結果が表示されない")
                        return False
                else:
                    print(f"❌ API有効時: HTTPエラー {result_response.status_code}")
                    return False
            else:
                print("❌ CSRFトークンが見つかりません")
                return False
        else:
            print(f"❌ フォーム取得エラー: {form_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API有効時テストエラー: {e}")
        return False

def test_api_disabled():
    """
    API無効時のテスト
    """
    print("\n=== API無効時テスト ===")
    
    # 環境変数をAPI無効に設定
    env_path = Path("django_app/.env")
    with open(env_path, "w") as f:
        f.write("USE_MODEL_API=false\n")
        f.write("FASTAPI_URL=http://localhost:8000\n")
        f.write("FASTAPI_TIMEOUT=10\n")
    
    print("✅ .env設定: USE_MODEL_API=false")
    
    # Django再起動を促す
    print("⚠️ Django サーバーを再起動してください")
    input("再起動後、Enterキーを押してください...")
    
    # テスト実行
    session = requests.Session()
    
    try:
        # フォーム取得
        form_response = session.get("http://localhost:8080/valuation/", timeout=5)
        
        if form_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form_response.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                
                # フォーム送信
                form_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'building_area': 80.0,
                    'land_area': 120.0,
                    'building_age': 10,
                    'ward_name': '世田谷区',
                    'year': 2024,
                    'quarter': 1
                }
                
                result_response = session.post(
                    "http://localhost:8080/valuation/result/",
                    data=form_data,
                    timeout=10
                )
                
                if result_response.status_code == 200:
                    if '現在、査定APIは利用できません' in result_response.text:
                        print("✅ API無効時: 正常にエラーメッセージ表示")
                        return True
                    elif 'メンテナンス中' in result_response.text:
                        print("✅ API無効時: メンテナンス中メッセージ表示")
                        return True
                    else:
                        print("❌ API無効時: エラーメッセージが表示されない")
                        print("Response preview:", result_response.text[:500])
                        return False
                else:
                    print(f"❌ API無効時: HTTPエラー {result_response.status_code}")
                    return False
            else:
                print("❌ CSRFトークンが見つかりません")
                return False
        else:
            print(f"❌ フォーム取得エラー: {form_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API無効時テストエラー: {e}")
        return False

def test_api_connection_error():
    """
    API接続エラー時のテスト
    """
    print("\n=== API接続エラー時テスト ===")
    
    # 環境変数を存在しないURLに設定
    env_path = Path("django_app/.env")
    with open(env_path, "w") as f:
        f.write("USE_MODEL_API=true\n")
        f.write("FASTAPI_URL=http://localhost:9999\n")  # 存在しないポート
        f.write("FASTAPI_TIMEOUT=3\n")  # 短いタイムアウト
    
    print("✅ .env設定: FASTAPI_URL=http://localhost:9999 (存在しない)")
    
    # Django再起動を促す
    print("⚠️ Django サーバーを再起動してください")
    input("再起動後、Enterキーを押してください...")
    
    # テスト実行
    session = requests.Session()
    
    try:
        # フォーム取得
        form_response = session.get("http://localhost:8080/valuation/", timeout=5)
        
        if form_response.status_code == 200:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form_response.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                
                # フォーム送信
                form_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'building_area': 80.0,
                    'land_area': 120.0,
                    'building_age': 10,
                    'ward_name': '世田谷区',
                    'year': 2024,
                    'quarter': 1
                }
                
                result_response = session.post(
                    "http://localhost:8080/valuation/result/",
                    data=form_data,
                    timeout=15
                )
                
                if result_response.status_code == 200:
                    if '接続エラー' in result_response.text or '接続できません' in result_response.text:
                        print("✅ 接続エラー時: 正常にエラーメッセージ表示")
                        return True
                    else:
                        print("❌ 接続エラー時: エラーメッセージが表示されない")
                        print("Response preview:", result_response.text[:500])
                        return False
                else:
                    print(f"❌ 接続エラー時: HTTPエラー {result_response.status_code}")
                    return False
            else:
                print("❌ CSRFトークンが見つかりません")
                return False
        else:
            print(f"❌ フォーム取得エラー: {form_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー時テストエラー: {e}")
        return False

def restore_original_settings():
    """
    元の設定に戻す
    """
    print("\n=== 設定を元に戻す ===")
    env_path = Path("django_app/.env")
    with open(env_path, "w") as f:
        f.write("USE_MODEL_API=true\n")
        f.write("FASTAPI_URL=http://localhost:8000\n")
        f.write("FASTAPI_TIMEOUT=10\n")
    
    print("✅ .env設定を元に戻しました")

def main():
    """
    メイン実行
    """
    print("🧪 API切り替え機能テスト")
    print("="*50)
    
    # サーバー起動確認
    try:
        response = requests.get("http://localhost:8080/", timeout=3)
        print("✅ Django サーバー起動確認")
    except:
        print("❌ Django サーバーが起動していません")
        return
    
    results = []
    
    # テスト実行
    results.append(test_api_enabled())
    results.append(test_api_disabled())
    results.append(test_api_connection_error())
    
    # 設定復元
    restore_original_settings()
    
    # 結果サマリー
    print("\n" + "="*50)
    print("🧪 テスト結果サマリー")
    print("="*50)
    
    test_names = [
        "API有効時テスト",
        "API無効時テスト", 
        "接続エラー時テスト"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{i+1}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 全テスト成功! ({success_count}/{total_count})")
    else:
        print(f"\n⚠️ 一部テスト失敗 ({success_count}/{total_count})")
    
    print(f"\n🕒 テスト完了: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n⚠️ Django サーバーを再起動して元の設定を反映してください")

if __name__ == "__main__":
    main()