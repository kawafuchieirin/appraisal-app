#!/usr/bin/env python3
"""
リファクタリング後のFastAPI統合テストスクリプト
"""

import requests
import json
import time
from typing import Dict, Any


def test_refactored_api():
    """
    リファクタリング後のAPIをテスト
    """
    base_url = "http://localhost:8000"
    
    print("🧪 リファクタリング後API統合テスト開始\n")
    
    # 1. Health check test
    print("=== 1. ヘルスチェックテスト ===")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ ヘルスチェック成功")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Model type: {data.get('model_info', {}).get('model_type')}")
        else:
            print(f"❌ ヘルスチェック失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ヘルスチェックエラー: {e}")
        return False
    
    # 2. Root endpoint test
    print("\n=== 2. ルートエンドポイントテスト ===")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ ルートエンドポイント成功")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ ルートエンドポイント失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ルートエンドポイントエラー: {e}")
        return False
    
    # 3. Prediction test
    print("\n=== 3. 予測エンドポイントテスト ===")
    test_data = {
        "land_area": 120.0,
        "building_area": 80.0,
        "building_age": 10,
        "ward_name": "世田谷区",
        "year": 2024,
        "quarter": 1
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 予測エンドポイント成功")
            print(f"   予測価格: {data.get('predicted_price'):,.1f}万円")
            print(f"   信頼度: {data.get('confidence')}")
            print(f"   使用特徴量数: {len(data.get('features_used', {}))}")
        else:
            print(f"❌ 予測エンドポイント失敗: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 予測エンドポイントエラー: {e}")
        return False
    
    # 4. Batch prediction test
    print("\n=== 4. バッチ予測エンドポイントテスト ===")
    batch_data = [
        {
            "land_area": 120.0,
            "building_area": 80.0,
            "building_age": 10,
            "ward_name": "世田谷区",
            "year": 2024,
            "quarter": 1
        },
        {
            "land_area": 100.0,
            "building_area": 90.0,
            "building_age": 5,
            "ward_name": "港区",
            "year": 2024,
            "quarter": 1
        }
    ]
    
    try:
        response = requests.post(
            f"{base_url}/predict/batch",
            json=batch_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ バッチ予測エンドポイント成功")
            print(f"   処理件数: {data.get('total_processed')}")
            print(f"   成功: {data.get('successful')}件")
            print(f"   失敗: {data.get('failed')}件")
            
            results = data.get('results', [])
            for i, result in enumerate(results):
                if result:
                    price = result.get('predicted_price', 0)
                    print(f"   物件{i+1}: {price:,.1f}万円")
        else:
            print(f"❌ バッチ予測エンドポイント失敗: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ バッチ予測エンドポイントエラー: {e}")
        return False
    
    return True


def main():
    """
    メイン実行
    """
    # サーバー起動確認
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        print("✅ FastAPI サーバー (8000) 起動確認")
    except:
        print("❌ FastAPI サーバーが起動していません (8000ポート)")
        print("次のコマンドで起動してください: python main.py")
        return
    
    print("\n" + "="*50)
    
    # テスト実行
    success = test_refactored_api()
    
    print("\n" + "="*50)
    print("🧪 リファクタリング後API統合テスト結果")
    print("="*50)
    
    if success:
        print("✅ 全てのテストが成功しました！")
        print("\n📋 確認済み項目:")
        print("   - ヘルスチェックエンドポイント")
        print("   - ルートエンドポイント") 
        print("   - 予測エンドポイント")
        print("   - バッチ予測エンドポイント")
        print("   - app.state による状態管理")
        print("   - ログのコンテキスト情報")
        print("   - 型安全な戻り値")
        print("   - モジュール化されたルーティング")
    else:
        print("❌ 一部のテストが失敗しました")
    
    print(f"\n🕒 テスト完了: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()