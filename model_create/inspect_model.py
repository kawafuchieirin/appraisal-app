#!/usr/bin/env python3
"""
モデルの詳細検査スクリプト
"""

import joblib
import numpy as np

def inspect_model():
    """
    モデルの詳細情報を表示
    """
    try:
        # モデル読み込み
        model = joblib.load('models/model.joblib')
        scaler = joblib.load('models/scaler.joblib')
        feature_info = joblib.load('models/feature_info.joblib')
        
        print("=== モデル詳細情報 ===")
        print(f"モデルタイプ: {type(model).__name__}")
        print(f"切片 (intercept): {model.intercept_:.2f}万円")
        print(f"特徴量数: {len(model.coef_)}")
        
        print("\n=== 重要な係数 (上位10個) ===")
        feature_names = feature_info['feature_columns']
        coefficients = model.coef_
        
        # 係数の絶対値でソート
        coef_abs = np.abs(coefficients)
        sorted_indices = np.argsort(coef_abs)[::-1]
        
        for i in range(min(10, len(sorted_indices))):
            idx = sorted_indices[i]
            feature_name = feature_names[idx]
            coef_value = coefficients[idx]
            print(f"  {feature_name:20s}: {coef_value:8.2f}万円")
        
        print("\n=== 区別係数 ===")
        for i, feature_name in enumerate(feature_names):
            if feature_name.startswith('ward_'):
                coef_value = coefficients[i]
                ward_name = feature_name.replace('ward_', '')
                print(f"  {ward_name:10s}: {coef_value:8.2f}万円")
        
        print("\n=== スケーラー情報 ===")
        print(f"平均値 (mean): {scaler.mean_[:5]}...")
        print(f"標準偏差 (scale): {scaler.scale_[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def test_prediction_breakdown():
    """
    予測の内訳を詳細表示
    """
    try:
        model = joblib.load('models/model.joblib')
        scaler = joblib.load('models/scaler.joblib')
        feature_info = joblib.load('models/feature_info.joblib')
        
        # テストデータ
        test_data = {
            'building_area': 80.0,
            'land_area': 120.0,
            'building_age': 10,
            'ward_name': '世田谷区',
            'year': 2024,
            'quarter': 1
        }
        
        print("\n=== 予測計算の詳細 ===")
        print(f"テストデータ: {test_data}")
        
        # 特徴量ベクトル作成（簡略版）
        feature_names = feature_info['feature_columns']
        feature_vector = np.zeros(len(feature_names))
        
        # 基本特徴量設定
        mappings = {
            'building_area': test_data['building_area'],
            'land_area': test_data['land_area'],
            'building_age': test_data['building_age'],
            'year': test_data['year'],
            'quarter': test_data['quarter'],
            'area_ratio': test_data['building_area'] / test_data['land_area']
        }
        
        # 区名設定
        ward_feature = f"ward_{test_data['ward_name']}"
        if ward_feature in feature_names:
            ward_idx = feature_names.index(ward_feature)
            feature_vector[ward_idx] = 1.0
        
        # 数値特徴量設定
        for feature_name, value in mappings.items():
            if feature_name in feature_names:
                idx = feature_names.index(feature_name)
                feature_vector[idx] = value
        
        print(f"\n元の特徴量ベクトル (0以外のみ):")
        for i, value in enumerate(feature_vector):
            if value != 0:
                print(f"  {feature_names[i]:20s}: {value:8.2f}")
        
        # 標準化
        feature_scaled = scaler.transform([feature_vector])[0]
        
        print(f"\n標準化後の特徴量 (0以外のみ):")
        for i, value in enumerate(feature_scaled):
            if abs(value) > 0.001:
                print(f"  {feature_names[i]:20s}: {value:8.4f}")
        
        # 予測計算の内訳
        print(f"\n=== 予測計算内訳 ===")
        print(f"切片: {model.intercept_:.2f}万円")
        
        total_contribution = model.intercept_
        for i, value in enumerate(feature_scaled):
            if abs(value) > 0.001:
                contribution = model.coef_[i] * value
                total_contribution += contribution
                print(f"  {feature_names[i]:20s}: {model.coef_[i]:8.2f} × {value:6.4f} = {contribution:8.2f}万円")
        
        print(f"\n最終予測価格: {total_contribution:.2f}万円")
        
        # 実際のモデル予測と比較
        actual_prediction = model.predict([feature_scaled])[0]
        print(f"model.predict()結果: {actual_prediction:.2f}万円")
        print(f"計算差異: {abs(total_contribution - actual_prediction):.6f}")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    inspect_model()
    test_prediction_breakdown()