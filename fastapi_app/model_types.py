"""
型定義モジュール - 予測結果とレスポンス構造
"""

from typing import TypedDict, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from predict_schema import PredictResponse


class PredictResult(TypedDict):
    """予測処理の戻り値型定義"""
    predicted_price: float
    confidence: Optional[float]
    features_used: Optional[Dict[str, float]]


class BatchPredictResponse(BaseModel):
    """バッチ予測レスポンスのPydanticモデル"""
    results: List[Optional[PredictResponse]] = Field(..., description="予測結果のリスト")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="エラー情報のリスト")
    total_processed: int = Field(..., description="処理された総件数")
    successful: int = Field(..., description="成功件数")
    failed: int = Field(..., description="失敗件数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "predicted_price": 8500.0,
                        "confidence": 0.85,
                        "features_used": {
                            "building_area": 80.0,
                            "land_area": 120.0
                        }
                    },
                    None  # エラーの場合
                ],
                "errors": [
                    {
                        "index": 1,
                        "error": "Invalid ward name",
                        "input": {"ward_name": "無効区名"}
                    }
                ],
                "total_processed": 2,
                "successful": 1,
                "failed": 1
            }
        }


class ErrorDetail(TypedDict):
    """エラー詳細の型定義"""
    index: int
    error: str
    input: Dict[str, Any]