"""
不動産価格予測API用の入力スキーマ定義
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class PredictRequest(BaseModel):
    """
    予測リクエストのスキーマ
    """
    land_area: float = Field(..., gt=0, description="土地面積（㎡）")
    building_area: float = Field(..., gt=0, description="建物面積（㎡）")
    building_age: float = Field(..., ge=0, le=100, description="築年数（年）")
    ward_name: str = Field(..., description="区名（例：世田谷区）")
    district: Optional[str] = Field(None, description="地区名（詳細）")
    year: Optional[int] = Field(2024, ge=2020, le=2030, description="査定年")
    quarter: Optional[int] = Field(1, ge=1, le=4, description="四半期")

    @validator('ward_name')
    def validate_ward_name(cls, v):
        """
        東京23区の区名バリデーション
        """
        valid_wards = {
            "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
            "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
            "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
        }
        
        if v not in valid_wards:
            raise ValueError(f"Invalid ward name. Must be one of: {', '.join(sorted(valid_wards))}")
        
        return v

    @validator('district', pre=True)
    def validate_district(cls, v, values):
        """
        地区名バリデーション（空文字列の場合はNoneに変換）
        """
        if v == "" or v is None:
            # 区名から地区名を生成
            ward_name = values.get('ward_name', '')
            if ward_name:
                return f"{ward_name}_1丁目"
            return None
        return v

    class Config:
        schema_extra = {
            "example": {
                "land_area": 120.0,
                "building_area": 80.0,
                "building_age": 10,
                "ward_name": "世田谷区",
                "district": "世田谷区_1丁目",
                "year": 2024,
                "quarter": 1
            }
        }


class PredictResponse(BaseModel):
    """
    予測レスポンスのスキーマ
    """
    predicted_price: float = Field(..., description="予測価格（万円）")
    confidence: Optional[float] = Field(None, description="信頼度（0-1）")
    features_used: Optional[dict] = Field(None, description="使用された特徴量")
    
    class Config:
        schema_extra = {
            "example": {
                "predicted_price": 8500.0,
                "confidence": 0.85,
                "features_used": {
                    "building_area": 80.0,
                    "land_area": 120.0,
                    "building_age": 10,
                    "ward_世田谷区": 1
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    エラーレスポンスのスキーマ
    """
    error: str = Field(..., description="エラーメッセージ")
    detail: Optional[str] = Field(None, description="詳細情報")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Prediction failed",
                "detail": "Model not loaded properly"
            }
        }