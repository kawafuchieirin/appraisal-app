#!/usr/bin/env python3
"""
不動産価格予測のための重回帰分析モデル訓練スクリプト
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class RealEstateModelTrainer:
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
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        print(f"Loading data from: {self.data_path}")
        df = pd.read_csv(self.data_path)
        
        print(f"Data shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        特徴量エンジニアリング
        """
        print("Preparing features...")
        
        # 基本特徴量
        feature_df = df.copy()
        
        # 数値特徴量
        numeric_features = []
        
        # 建物面積
        if 'building_area' in feature_df.columns:
            feature_df['building_area'] = pd.to_numeric(feature_df['building_area'], errors='coerce')
            numeric_features.append('building_area')
        
        # 土地面積
        if 'land_area' in feature_df.columns:
            feature_df['land_area'] = pd.to_numeric(feature_df['land_area'], errors='coerce')
            numeric_features.append('land_area')
        
        # 築年数
        if 'building_age' in feature_df.columns:
            feature_df['building_age'] = pd.to_numeric(feature_df['building_age'], errors='coerce')
            numeric_features.append('building_age')
        
        # 年・四半期
        if 'year' in feature_df.columns:
            feature_df['year'] = pd.to_numeric(feature_df['year'], errors='coerce')
            numeric_features.append('year')
        
        if 'quarter' in feature_df.columns:
            feature_df['quarter'] = pd.to_numeric(feature_df['quarter'], errors='coerce')
            numeric_features.append('quarter')
        
        # カテゴリ特徴量のエンコーディング
        categorical_features = []
        
        # 区名をOne-hot encoding
        if 'ward_name' in feature_df.columns:
            ward_dummies = pd.get_dummies(feature_df['ward_name'], prefix='ward')
            feature_df = pd.concat([feature_df, ward_dummies], axis=1)
            categorical_features.extend(ward_dummies.columns.tolist())
        
        # 地区名をLabel encoding（カテゴリが多い場合）
        if 'district' in feature_df.columns:
            le_district = LabelEncoder()
            feature_df['district_encoded'] = le_district.fit_transform(feature_df['district'].astype(str))
            self.label_encoders['district'] = le_district
            numeric_features.append('district_encoded')
        
        # 特徴量の組み合わせ
        if 'building_area' in feature_df.columns and 'land_area' in feature_df.columns:
            feature_df['area_ratio'] = feature_df['building_area'] / (feature_df['land_area'] + 1e-6)
            numeric_features.append('area_ratio')
        
        if 'building_area' in feature_df.columns:
            feature_df['price_per_area'] = feature_df[self.target_column] / (feature_df['building_area'] + 1e-6)
        
        # 最終的な特徴量列
        self.feature_columns = numeric_features + categorical_features
        
        print(f"Selected features ({len(self.feature_columns)}): {self.feature_columns[:10]}...")
        
        return feature_df
    
    def train_model(self, df: pd.DataFrame):
        """
        モデル訓練
        """
        print("Training regression model...")
        
        # 特徴量とターゲット変数を分離
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        # 欠損値を除去
        mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[mask]
        y = y[mask]
        
        print(f"Training data shape: {X.shape}")
        print(f"Target data shape: {y.shape}")
        
        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 特徴量の標準化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # モデル訓練
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)
        
        # 予測
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # 評価
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        print("\n=== Model Evaluation ===")
        print(f"Training R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        print(f"Training RMSE: {train_rmse:,.0f}")
        print(f"Test RMSE: {test_rmse:,.0f}")
        print(f"Training MAE: {train_mae:,.0f}")
        print(f"Test MAE: {test_mae:,.0f}")
        
        # 特徴量重要度（回帰係数）
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'coefficient': self.model.coef_
        })
        feature_importance['abs_coefficient'] = np.abs(feature_importance['coefficient'])
        feature_importance = feature_importance.sort_values('abs_coefficient', ascending=False)
        
        print("\n=== Top 10 Feature Importance ===")
        print(feature_importance.head(10))
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'feature_importance': feature_importance
        }
    
    def save_model(self, model_dir: str = "models"):
        """
        モデルと前処理器を保存
        """
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # モデル保存
        model_path = os.path.join(model_dir, "model.joblib")
        joblib.dump(self.model, model_path)
        print(f"Model saved to: {model_path}")
        
        # スケーラー保存
        scaler_path = os.path.join(model_dir, "scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        print(f"Scaler saved to: {scaler_path}")
        
        # 特徴量情報保存
        feature_info = {
            'feature_columns': self.feature_columns,
            'label_encoders': self.label_encoders,
            'target_column': self.target_column
        }
        feature_path = os.path.join(model_dir, "feature_info.joblib")
        joblib.dump(feature_info, feature_path)
        print(f"Feature info saved to: {feature_path}")
    
    def load_model(self, model_dir: str = "models"):
        """
        保存されたモデルを読み込み
        """
        model_path = os.path.join(model_dir, "model.joblib")
        scaler_path = os.path.join(model_dir, "scaler.joblib")
        feature_path = os.path.join(model_dir, "feature_info.joblib")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        feature_info = joblib.load(feature_path)
        self.feature_columns = feature_info['feature_columns']
        self.label_encoders = feature_info['label_encoders']
        self.target_column = feature_info['target_column']
        
        print("Model loaded successfully!")
    
    def predict(self, features: dict) -> float:
        """
        予測を実行
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained or loaded")
        
        # 特徴量ベクトルを作成
        feature_vector = np.zeros(len(self.feature_columns))
        
        for i, feature_name in enumerate(self.feature_columns):
            if feature_name in features:
                feature_vector[i] = features[feature_name]
        
        # 標準化
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # 予測
        prediction = self.model.predict(feature_vector_scaled)[0]
        
        return prediction

def main():
    """
    メイン実行関数
    """
    try:
        trainer = RealEstateModelTrainer()
        
        # データ読み込み
        df = trainer.load_data()
        
        if df.empty:
            print("No data available for training.")
            return
        
        # 特徴量準備
        df_features = trainer.prepare_features(df)
        
        # モデル訓練
        results = trainer.train_model(df_features)
        
        # モデル保存
        trainer.save_model()
        
        print("\n=== Model Training Completed Successfully! ===")
        print(f"Final Test R²: {results['test_r2']:.4f}")
        print(f"Final Test RMSE: {results['test_rmse']:,.0f}")
        
        # 予測例
        print("\n=== Prediction Example ===")
        sample_features = {
            'building_area': 100.0,
            'land_area': 150.0,
            'building_age': 10,
            'year': 2024,
            'quarter': 1,
            'ward_千代田区': 1  # 千代田区の場合
        }
        
        try:
            prediction = trainer.predict(sample_features)
            print(f"Sample prediction: {prediction:,.0f} 万円")
        except Exception as e:
            print(f"Prediction example failed: {e}")
        
    except Exception as e:
        print(f"Error in training: {e}")
        raise

if __name__ == "__main__":
    main()