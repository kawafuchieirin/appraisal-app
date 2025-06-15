#!/usr/bin/env python3
"""
東京23区の不動産取引価格データ取得スクリプト
国土交通省 不動産情報ライブラリ API4 を使用
"""

import os
import requests
import pandas as pd
import time
from typing import List, Dict, Any
import json

# 東京23区の市区町村コード
TOKYO_23KU_CODES = {
    "千代田区": "13101",
    "中央区": "13102", 
    "港区": "13103",
    "新宿区": "13104",
    "文京区": "13105",
    "台東区": "13106",
    "墨田区": "13107",
    "江東区": "13108",
    "品川区": "13109",
    "目黒区": "13110",
    "大田区": "13111",
    "世田谷区": "13112",
    "渋谷区": "13113",
    "中野区": "13114",
    "杉並区": "13115",
    "豊島区": "13116",
    "北区": "13117",
    "荒川区": "13118",
    "板橋区": "13119",
    "練馬区": "13120",
    "足立区": "13121",
    "葛飾区": "13122",
    "江戸川区": "13123"
}

# 対象年度
TARGET_YEARS = [2020, 2021, 2022, 2023, 2024]
TARGET_QUARTERS = [1, 2, 3, 4]

class TokyoRealEstateFetcher:
    def __init__(self):
        self.api_key = os.getenv('MLIT_API_KEY')
        if not self.api_key:
            raise ValueError("MLIT_API_KEY environment variable is required")
        
        self.base_url = "https://www.reinfolib.mlit.go.jp/ex-api/external/XIT001"
        self.session = requests.Session()
        # 正しいヘッダー認証を設定
        self.session.headers.update({
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Accept-Encoding': 'gzip'
        })
        
    def fetch_transaction_data(self, area_code: str, year: int, quarter: int) -> List[Dict[Any, Any]]:
        """
        指定した地域・期間の取引価格データを取得
        """
        params = {
            'area': area_code,
            'year': year,
            'quarter': quarter
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                return data['data']
            else:
                print(f"No data found for {area_code}, {year}Q{quarter}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {area_code}, {year}Q{quarter}: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {area_code}, {year}Q{quarter}: {e}")
            return []
    
    def fetch_all_tokyo_data(self) -> pd.DataFrame:
        """
        東京23区の全データを取得してDataFrameとして返す
        """
        all_data = []
        total_requests = len(TOKYO_23KU_CODES) * len(TARGET_YEARS) * len(TARGET_QUARTERS)
        request_count = 0
        
        print(f"Starting data collection for Tokyo 23 wards...")
        print(f"Total API requests planned: {total_requests}")
        
        for ward_name, area_code in TOKYO_23KU_CODES.items():
            print(f"\nFetching data for {ward_name} ({area_code})...")
            
            for year in TARGET_YEARS:
                for quarter in TARGET_QUARTERS:
                    request_count += 1
                    print(f"  Progress: {request_count}/{total_requests} - {year}Q{quarter}")
                    
                    # API rate limiting
                    time.sleep(0.5)
                    
                    data = self.fetch_transaction_data(area_code, year, quarter)
                    
                    for record in data:
                        # レコードに区名、年、四半期を追加
                        record['ward_name'] = ward_name
                        record['ward_code'] = area_code
                        record['year'] = year
                        record['quarter'] = quarter
                        all_data.append(record)
        
        print(f"\nData collection completed!")
        print(f"Total records collected: {len(all_data)}")
        
        if all_data:
            return pd.DataFrame(all_data)
        else:
            print("No data collected!")
            return pd.DataFrame()
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データの前処理
        """
        if df.empty:
            return df
            
        print("Starting data preprocessing...")
        
        # 基本統計
        print(f"Original data shape: {df.shape}")
        
        # 必要な列を選択・リネーム（API4のレスポンス形式に合わせて調整が必要）
        # ここではサンプルの列名を使用。実際のAPIレスポンスに合わせて修正が必要
        try:
            # 価格関連
            if 'TradePrice' in df.columns:
                df['price'] = pd.to_numeric(df['TradePrice'], errors='coerce')
            elif '取引価格（総額）' in df.columns:
                df['price'] = pd.to_numeric(df['取引価格（総額）'], errors='coerce')
            
            # 面積関連  
            if 'Area' in df.columns:
                df['building_area'] = pd.to_numeric(df['Area'], errors='coerce')
            elif '面積' in df.columns:
                df['building_area'] = pd.to_numeric(df['面積'], errors='coerce')
                
            # 土地面積
            if 'LandArea' in df.columns:
                df['land_area'] = pd.to_numeric(df['LandArea'], errors='coerce')
            elif '土地の形状（面積）' in df.columns:
                df['land_area'] = pd.to_numeric(df['土地の形状（面積）'], errors='coerce')
            
            # 築年数
            if 'BuildingYear' in df.columns:
                df['building_age'] = pd.to_numeric(df['BuildingYear'], errors='coerce')
            elif '建築年' in df.columns:
                current_year = 2024
                df['building_age'] = current_year - pd.to_numeric(df['建築年'], errors='coerce')
            
            # 地区名
            if 'DistrictName' in df.columns:
                df['district'] = df['DistrictName']
            elif '地区名' in df.columns:
                df['district'] = df['地区名']
            
        except Exception as e:
            print(f"Column processing error: {e}")
            print("Available columns:", df.columns.tolist())
        
        # 欠損値を除去
        original_len = len(df)
        df = df.dropna(subset=['price'])
        print(f"Removed {original_len - len(df)} records with missing price")
        
        # 異常値を除去（価格が0以下または極端に高い場合）
        if 'price' in df.columns:
            df = df[df['price'] > 0]
            df = df[df['price'] < df['price'].quantile(0.99)]  # 上位1%を除去
        
        print(f"Final data shape: {df.shape}")
        return df
    
    def save_data(self, df: pd.DataFrame, filename: str = "tokyo_23ku_2020_2024.csv"):
        """
        データをCSVファイルに保存
        """
        filepath = os.path.join("data", filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Data saved to: {filepath}")
        
        # 基本統計情報を表示
        if not df.empty:
            print("\nData Summary:")
            print(f"Total records: {len(df)}")
            if 'ward_name' in df.columns:
                print(f"Wards covered: {df['ward_name'].nunique()}")
                print("Records per ward:")
                print(df['ward_name'].value_counts().head())
            if 'year' in df.columns:
                print("Records per year:")
                print(df['year'].value_counts().sort_index())

def main():
    """
    メイン実行関数
    """
    try:
        fetcher = TokyoRealEstateFetcher()
        
        # データ取得
        df = fetcher.fetch_all_tokyo_data()
        
        if df.empty:
            print("No data was collected. Please check API key and connection.")
            return
        
        # 前処理
        df_processed = fetcher.preprocess_data(df)
        
        # 保存
        fetcher.save_data(df_processed)
        
        print("\nData collection and preprocessing completed successfully!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()