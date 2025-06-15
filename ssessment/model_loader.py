"""
機械学習モデルの読み込みと管理
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Optional
import logging


class ModelLoader:
    """
    機械学習モデルとスケーラーの読み込み・管理クラス
    """
    
    def __init__(self, model_dir: str = "../model_create/models"):
        """
        モデルローダーの初期化
        
        Args:
            model_dir: モデルファイルが格納されているディレクトリ
        """
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.feature_info = None
        self.logger = logging.getLogger(__name__)
        
        # 起動時にモデルを読み込み
        self.load_models()
    
    def load_models(self) -> bool:
        """
        モデル、スケーラー、特徴量情報を読み込み
        
        Returns:
            bool: 読み込み成功の可否
        """
        try:
            model_path = os.path.join(self.model_dir, "model.joblib")
            scaler_path = os.path.join(self.model_dir, "scaler.joblib")
            feature_path = os.path.join(self.model_dir, "feature_info.joblib")
            
            # ファイル存在確認
            if not all(os.path.exists(path) for path in [model_path, scaler_path, feature_path]):
                missing_files = [
                    path for path in [model_path, scaler_path, feature_path] 
                    if not os.path.exists(path)
                ]
                raise FileNotFoundError(f"Missing model files: {missing_files}")
            
            # モデル読み込み
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_info = joblib.load(feature_path)
            
            self.logger.info("Models loaded successfully")
            self.logger.info(f"Feature count: {len(self.feature_info['feature_columns'])}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def prepare_features(self, request_data: Dict[str, Any]) -> np.ndarray:
        """
        入力データから特徴量ベクトルを準備
        
        Args:
            request_data: API リクエストデータ
            
        Returns:
            np.ndarray: 特徴量ベクトル
        """
        if not self.is_loaded():
            raise RuntimeError("Models not loaded")
        
        feature_columns = self.feature_info['feature_columns']
        feature_vector = np.zeros(len(feature_columns))
        
        # 基本的な数値特徴量
        numeric_mappings = {
            'building_area': request_data.get('building_area', 0),
            'land_area': request_data.get('land_area', 0),
            'building_age': request_data.get('building_age', 0),
            'year': request_data.get('year', 2024),
            'quarter': request_data.get('quarter', 1)
        }
        
        # 面積比率の計算
        if 'area_ratio' in feature_columns:
            building_area = numeric_mappings['building_area']
            land_area = numeric_mappings['land_area']
            numeric_mappings['area_ratio'] = building_area / (land_area + 1e-6)
        
        # 地区エンコーディング
        district = request_data.get('district')
        if district and 'district_encoded' in feature_columns:
            label_encoder = self.feature_info.get('label_encoders', {}).get('district')
            if label_encoder:
                try:
                    encoded_district = label_encoder.transform([district])[0]
                    numeric_mappings['district_encoded'] = encoded_district
                except ValueError:
                    # 未知の地区の場合は0を設定
                    numeric_mappings['district_encoded'] = 0
            else:
                numeric_mappings['district_encoded'] = 0
        
        # 区名のOne-hot encoding
        ward_name = request_data.get('ward_name', '')
        if ward_name:
            ward_column = f'ward_{ward_name}'
            if ward_column in feature_columns:
                ward_index = feature_columns.index(ward_column)
                feature_vector[ward_index] = 1
        
        # 数値特徴量の設定
        for feature_name, value in numeric_mappings.items():
            if feature_name in feature_columns:
                feature_index = feature_columns.index(feature_name)
                feature_vector[feature_index] = float(value)
        
        return feature_vector.reshape(1, -1)
    
    def predict(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        予測実行
        
        Args:
            request_data: API リクエストデータ
            
        Returns:
            Dict[str, Any]: 予測結果
        """
        if not self.is_loaded():
            raise RuntimeError("Models not loaded")
        
        try:
            # 特徴量準備
            features = self.prepare_features(request_data)
            
            # 標準化
            features_scaled = self.scaler.transform(features)
            
            # 予測実行
            prediction = self.model.predict(features_scaled)[0]
            
            # 予測値の妥当性チェック
            if prediction < 0:
                prediction = abs(prediction)
            
            # 使用された特徴量（デバッグ用）
            features_used = {}
            feature_columns = self.feature_info['feature_columns']
            for i, col in enumerate(feature_columns):
                if features[0][i] != 0:
                    features_used[col] = float(features[0][i])
            
            result = {
                'predicted_price': round(prediction, 1),
                'confidence': self._calculate_confidence(features),
                'features_used': features_used
            }
            
            self.logger.info(f"Prediction successful: {prediction:.1f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """
        信頼度の計算（簡易版）
        
        Args:
            features: 特徴量ベクトル
            
        Returns:
            float: 信頼度（0-1）
        """
        # 簡易的な信頼度計算
        # 実際には予測区間やアンサンブルモデルを使用する
        non_zero_features = np.count_nonzero(features)
        total_features = features.shape[1]
        
        # 特徴量の充実度に基づく信頼度
        feature_completeness = non_zero_features / total_features
        
        # 基本的な信頼度（0.7-0.95の範囲）
        confidence = 0.7 + (feature_completeness * 0.25)
        
        return round(min(confidence, 0.95), 3)
    
    def is_loaded(self) -> bool:
        """
        モデルが正常に読み込まれているかチェック
        
        Returns:
            bool: 読み込み状態
        """
        return all([
            self.model is not None,
            self.scaler is not None,
            self.feature_info is not None
        ])
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        モデル情報の取得
        
        Returns:
            Dict[str, Any]: モデル情報
        """
        if not self.is_loaded():
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_type": type(self.model).__name__,
            "feature_count": len(self.feature_info['feature_columns']),
            "features": self.feature_info['feature_columns'][:10],  # 先頭10個
            "scaler_type": type(self.scaler).__name__
        }