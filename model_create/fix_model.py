#!/usr/bin/env python3
"""
モデルの修正版 - 数値安定性を改善
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge  # 正則化付き回帰
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class ImprovedRealEstateModelTrainer:
    def __init__(self, data_path: str = "data/tokyo_23ku_2020_2024.csv"):
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = 'price'
        
    def load_data(self) -> pd.DataFrame:
        """
        CSVデータを読み込み
        """
        df = pd.read_csv(self.data_path)
        print(f"Data shape: {df.shape}")
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        改善された特徴量エンジニアリング
        """
        print("Preparing features with improved stability...")
        
        feature_df = df.copy()
        
        # 基本数値特徴量
        numeric_features = ['building_area', 'land_area', 'building_age', 'year', 'quarter']
        
        # 欠損値処理
        for col in numeric_features:
            if col in feature_df.columns:
                feature_df[col] = pd.to_numeric(feature_df[col], errors='coerce').fillna(0)
        
        # 派生特徴量
        if 'building_area' in feature_df.columns and 'land_area' in feature_df.columns:
            feature_df['area_ratio'] = feature_df['building_area'] / (feature_df['land_area'] + 1e-6)
            feature_df['total_area'] = feature_df['building_area'] + feature_df['land_area']
            numeric_features.extend(['area_ratio', 'total_area'])
        
        # 区名を数値エンコーディング（One-hotの代わり）
        if 'ward_name' in feature_df.columns:
            le_ward = LabelEncoder()
            feature_df['ward_encoded'] = le_ward.fit_transform(feature_df['ward_name'].astype(str))
            self.label_encoders['ward'] = le_ward
            numeric_features.append('ward_encoded')
        
        # 地区名エンコーディング
        if 'district' in feature_df.columns:
            le_district = LabelEncoder()
            feature_df['district_encoded'] = le_district.fit_transform(feature_df['district'].astype(str))
            self.label_encoders['district'] = le_district
            numeric_features.append('district_encoded')
        
        self.feature_columns = numeric_features
        print(f"Selected features ({len(self.feature_columns)}): {self.feature_columns}")
        
        return feature_df
    
    def train_model(self, df: pd.DataFrame):
        """
        正則化付き回帰モデルの訓練
        """
        print("Training Ridge regression model...")
        
        # 特徴量とターゲット変数を分離
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        # 欠損値を除去
        mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[mask]
        y = y[mask]
        
        print(f"Training data shape: {X.shape}")
        
        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 特徴量の標準化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Ridge回帰モデル（正則化あり）
        self.model = Ridge(alpha=100.0)  # 正則化パラメータ
        self.model.fit(X_train_scaled, y_train)
        
        # 予測
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # 評価
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        
        print("\n=== Improved Model Evaluation ===")
        print(f"Training R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        print(f"Training RMSE: {train_rmse:,.0f}")
        print(f"Test RMSE: {test_rmse:,.0f}")
        
        # 係数確認
        print(f"\nModel intercept: {self.model.intercept_:.2f}")
        print("\nFeature coefficients:")
        for i, feature in enumerate(self.feature_columns):
            print(f"  {feature:15s}: {self.model.coef_[i]:8.2f}")
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse
        }
    
    def save_model(self, model_dir: str = "models"):
        """
        改善されたモデルを保存
        """
        import os
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # 古いモデルをバックアップ
        import shutil
        backup_dir = f"{model_dir}_backup"
        if os.path.exists(model_dir):
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(model_dir, backup_dir)
            print(f"Old model backed up to: {backup_dir}")
        
        # 新しいモデル保存
        model_path = os.path.join(model_dir, "model.joblib")
        scaler_path = os.path.join(model_dir, "scaler.joblib")
        feature_path = os.path.join(model_dir, "feature_info.joblib")
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        feature_info = {
            'feature_columns': self.feature_columns,
            'label_encoders': self.label_encoders,
            'target_column': self.target_column,
            'model_type': 'Ridge'
        }
        joblib.dump(feature_info, feature_path)
        
        print(f"Improved model saved to: {model_dir}")

def main():
    """
    改善されたモデルの訓練と保存
    """
    try:
        trainer = ImprovedRealEstateModelTrainer()
        
        # データ読み込み
        df = trainer.load_data()
        
        # 特徴量準備
        df_features = trainer.prepare_features(df)
        
        # モデル訓練
        results = trainer.train_model(df_features)
        
        # モデル保存
        trainer.save_model()
        
        print("\n=== Improved Model Training Completed! ===")
        print(f"Final Test R²: {results['test_r2']:.4f}")
        print(f"Final Test RMSE: {results['test_rmse']:,.0f}")
        
    except Exception as e:
        print(f"Error in training: {e}")
        raise

if __name__ == "__main__":
    main()