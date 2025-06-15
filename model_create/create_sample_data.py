#!/usr/bin/env python3
"""
サンプル不動産データ生成スクリプト
実際のAPIデータが取得できない場合のフォールバック
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime

# 東京23区リスト
TOKYO_23KU = [
    "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
    "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
    "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
]

# 区ごとの価格レンジ（万円）
WARD_PRICE_RANGES = {
    "千代田区": (8000, 15000),
    "中央区": (7000, 12000),
    "港区": (8000, 20000),
    "新宿区": (5000, 10000),
    "文京区": (6000, 12000),
    "台東区": (4000, 8000),
    "墨田区": (3500, 7000),
    "江東区": (4000, 8000),
    "品川区": (5000, 10000),
    "目黒区": (6000, 12000),
    "大田区": (4000, 8000),
    "世田谷区": (5000, 10000),
    "渋谷区": (7000, 15000),
    "中野区": (4000, 8000),
    "杉並区": (4500, 8500),
    "豊島区": (4000, 8000),
    "北区": (3000, 6000),
    "荒川区": (3000, 6000),
    "板橋区": (3500, 7000),
    "練馬区": (3500, 7000),
    "足立区": (2500, 5000),
    "葛飾区": (2500, 5000),
    "江戸川区": (3000, 6000)
}

def generate_sample_data(num_records: int = 5000) -> pd.DataFrame:
    """
    サンプルデータを生成
    """
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for _ in range(num_records):
        # 基本情報
        ward_name = random.choice(TOKYO_23KU)
        year = random.choice([2020, 2021, 2022, 2023, 2024])
        quarter = random.choice([1, 2, 3, 4])
        
        # 建物面積（㎡）
        building_area = np.random.normal(70, 30)
        building_area = max(20, min(200, building_area))
        
        # 土地面積（㎡）
        land_area = np.random.normal(100, 40)
        land_area = max(30, min(300, land_area))
        
        # 築年数
        building_age = np.random.exponential(15)
        building_age = max(0, min(50, building_age))
        
        # 地区名（区内の架空の地区）
        district_num = random.randint(1, 5)
        district = f"{ward_name}_{district_num}丁目"
        
        # 価格計算（現実的な価格モデル）
        min_price, max_price = WARD_PRICE_RANGES[ward_name]
        
        # 基本価格
        base_price = np.random.uniform(min_price, max_price)
        
        # 面積による調整
        area_factor = (building_area / 70) * 0.8 + (land_area / 100) * 0.2
        
        # 築年数による調整（新しいほど高い）
        age_factor = max(0.5, 1.0 - (building_age / 50) * 0.4)
        
        # 年による調整（最近のほうが高い傾向）
        year_factor = 1.0 + (year - 2020) * 0.02
        
        # 最終価格
        price = base_price * area_factor * age_factor * year_factor
        
        # ランダムな変動を追加
        price *= np.random.normal(1.0, 0.1)
        price = max(1000, price)  # 最低1000万円
        
        record = {
            'price': round(price, 1),
            'building_area': round(building_area, 1),
            'land_area': round(land_area, 1),
            'building_age': round(building_age, 1),
            'ward_name': ward_name,
            'district': district,
            'year': year,
            'quarter': quarter
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def main():
    """
    メイン実行関数
    """
    print("Generating sample real estate data...")
    
    # サンプルデータ生成
    df = generate_sample_data(5000)
    
    # 基本統計表示
    print(f"\nGenerated {len(df)} records")
    print(f"Price range: {df['price'].min():.0f} - {df['price'].max():.0f}万円")
    print(f"Building area range: {df['building_area'].min():.1f} - {df['building_area'].max():.1f}㎡")
    print(f"Land area range: {df['land_area'].min():.1f} - {df['land_area'].max():.1f}㎡")
    print(f"Building age range: {df['building_age'].min():.1f} - {df['building_age'].max():.1f}年")
    
    print("\nRecords per ward:")
    print(df['ward_name'].value_counts().head(10))
    
    print("\nRecords per year:")
    print(df['year'].value_counts().sort_index())
    
    # CSV保存
    output_path = "data/tokyo_23ku_2020_2024.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nSample data saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    main()