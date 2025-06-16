#!/usr/bin/env python3
"""
FastAPI統合テストスクリプト
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

class APITester:
    """
    FastAPI エンドポイントの統合テスト
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def test_health_endpoint(self) -> bool:
        """
        ヘルスチェックエンドポイントのテスト
        """
        print("=== ヘルスチェックテスト ===")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ヘルスチェック成功")
                print(f"   Status: {data.get('status')}")
                print(f"   Model loaded: {data.get('model_loaded')}")
                print(f"   Model type: {data.get('model_info', {}).get('model_type')}")
                print(f"   Features: {data.get('model_info', {}).get('feature_count')}")
                
                self.test_results.append({
                    "test": "health_check",
                    "status": "pass",
                    "response_time": response.elapsed.total_seconds(),
                    "data": data
                })
                return True
            else:
                print(f"❌ ヘルスチェック失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ヘルスチェックエラー: {e}")
            return False
    
    def test_predict_endpoint(self, test_cases: List[Dict]) -> bool:
        """
        予測エンドポイントのテスト
        """
        print("\n=== 予測エンドポイントテスト ===")
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- テストケース {i}: {test_case['name']} ---")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=test_case['input'],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    predicted_price = data.get('predicted_price', 0)
                    confidence = data.get('confidence', 0)
                    features_used = data.get('features_used', {})
                    
                    print(f"✅ 予測成功")
                    print(f"   予測価格: {predicted_price:,.1f}万円")
                    print(f"   信頼度: {confidence:.3f}")
                    print(f"   レスポンス時間: {response_time:.3f}秒")
                    print(f"   使用特徴量数: {len(features_used)}")
                    
                    # 価格妥当性チェック
                    if 1000 <= predicted_price <= 50000:
                        print(f"   ✅ 価格範囲妥当")
                    else:
                        print(f"   ⚠️ 価格範囲要確認: {predicted_price}")
                    
                    # 信頼度チェック
                    if 0.5 <= confidence <= 1.0:
                        print(f"   ✅ 信頼度妥当")
                    else:
                        print(f"   ⚠️ 信頼度要確認: {confidence}")
                    
                    self.test_results.append({
                        "test": f"predict_case_{i}",
                        "name": test_case['name'],
                        "status": "pass",
                        "response_time": response_time,
                        "input": test_case['input'],
                        "output": data
                    })
                    
                else:
                    print(f"❌ 予測失敗: {response.status_code}")
                    print(f"   Response: {response.text}")
                    all_passed = False
                    
                    self.test_results.append({
                        "test": f"predict_case_{i}",
                        "name": test_case['name'],
                        "status": "fail",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    
            except Exception as e:
                print(f"❌ テストエラー: {e}")
                all_passed = False
                
                self.test_results.append({
                    "test": f"predict_case_{i}",
                    "name": test_case['name'],
                    "status": "error",
                    "error": str(e)
                })
        
        return all_passed
    
    def test_error_handling(self) -> bool:
        """
        エラーハンドリングのテスト
        """
        print("\n=== エラーハンドリングテスト ===")
        
        error_cases = [
            {
                "name": "不正な区名",
                "input": {
                    "land_area": 100.0,
                    "building_area": 80.0,
                    "building_age": 10,
                    "ward_name": "無効区名"
                },
                "expected_status": 422
            },
            {
                "name": "負の面積",
                "input": {
                    "land_area": -50.0,
                    "building_area": 80.0,
                    "building_age": 10,
                    "ward_name": "世田谷区"
                },
                "expected_status": 422
            },
            {
                "name": "必須フィールド不足",
                "input": {
                    "building_area": 80.0,
                    "building_age": 10,
                    "ward_name": "世田谷区"
                },
                "expected_status": 422
            }
        ]
        
        all_passed = True
        
        for case in error_cases:
            print(f"\n--- エラーケース: {case['name']} ---")
            
            try:
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=case['input'],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == case['expected_status']:
                    print(f"✅ 期待通りのエラー: {response.status_code}")
                else:
                    print(f"❌ 予期しないステータス: {response.status_code} (期待: {case['expected_status']})")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ テストエラー: {e}")
                all_passed = False
        
        return all_passed
    
    def test_batch_endpoint(self) -> bool:
        """
        バッチ予測エンドポイントのテスト
        """
        print("\n=== バッチ予測テスト ===")
        
        batch_input = [
            {
                "land_area": 120.0,
                "building_area": 80.0,
                "building_age": 10,
                "ward_name": "世田谷区"
            },
            {
                "land_area": 100.0,
                "building_area": 90.0,
                "building_age": 5,
                "ward_name": "港区"
            },
            {
                "land_area": 150.0,
                "building_area": 70.0,
                "building_age": 15,
                "ward_name": "杉並区"
            }
        ]
        
        try:
            response = requests.post(
                f"{self.base_url}/predict/batch",
                json=batch_input,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                successful = data.get('successful', 0)
                failed = data.get('failed', 0)
                
                print(f"✅ バッチ予測成功")
                print(f"   処理件数: {len(batch_input)}")
                print(f"   成功: {successful}件")
                print(f"   失敗: {failed}件")
                
                for i, result in enumerate(results):
                    if result:
                        price = result.get('predicted_price', 0)
                        print(f"   物件{i+1}: {price:,.1f}万円")
                
                return True
            else:
                print(f"❌ バッチ予測失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ バッチテストエラー: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """
        全テストの実行
        """
        print("🧪 FastAPI統合テスト開始\n")
        
        # テストケース定義
        test_cases = [
            {
                "name": "標準的な世田谷区物件",
                "input": {
                    "land_area": 120.0,
                    "building_area": 80.0,
                    "building_age": 10,
                    "ward_name": "世田谷区",
                    "year": 2024,
                    "quarter": 1
                }
            },
            {
                "name": "高級エリア港区物件",
                "input": {
                    "land_area": 100.0,
                    "building_area": 90.0,
                    "building_age": 5,
                    "ward_name": "港区",
                    "year": 2024,
                    "quarter": 1
                }
            },
            {
                "name": "築年数古い物件",
                "input": {
                    "land_area": 150.0,
                    "building_area": 70.0,
                    "building_age": 30,
                    "ward_name": "足立区",
                    "year": 2024,
                    "quarter": 1
                }
            },
            {
                "name": "小規模物件",
                "input": {
                    "land_area": 60.0,
                    "building_area": 45.0,
                    "building_age": 2,
                    "ward_name": "文京区",
                    "year": 2024,
                    "quarter": 1
                }
            }
        ]
        
        # テスト実行
        all_passed = True
        
        all_passed &= self.test_health_endpoint()
        all_passed &= self.test_predict_endpoint(test_cases)
        all_passed &= self.test_error_handling()
        all_passed &= self.test_batch_endpoint()
        
        # 結果サマリー
        print("\n" + "="*50)
        print("🧪 テスト結果サマリー")
        print("="*50)
        
        if all_passed:
            print("✅ 全テスト成功！")
        else:
            print("❌ 一部テスト失敗")
        
        # 詳細結果をJSONで保存
        self.save_results()
        
        return all_passed
    
    def save_results(self):
        """
        テスト結果をJSONファイルに保存
        """
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r.get('status') == 'pass']),
            "failed_tests": len([r for r in self.test_results if r.get('status') in ['fail', 'error']]),
            "results": self.test_results
        }
        
        with open('api_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 テスト結果を api_test_results.json に保存しました")

def main():
    """
    メイン実行関数
    """
    tester = APITester()
    
    # サーバー接続確認
    try:
        response = requests.get(f"{tester.base_url}/", timeout=5)
        if response.status_code != 200:
            print("❌ FastAPIサーバーが起動していません")
            print("先に 'python main.py' でサーバーを起動してください")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ FastAPIサーバーに接続できません")
        print("先に 'python main.py' でサーバーを起動してください")
        sys.exit(1)
    
    # テスト実行
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 全ての統合テストが成功しました！")
        sys.exit(0)
    else:
        print("\n⚠️ 一部のテストが失敗しました。詳細を確認してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()