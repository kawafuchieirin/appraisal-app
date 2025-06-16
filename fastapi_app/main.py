"""
不動産価格予測 FastAPI アプリケーション
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from mangum import Mangum

from predict_schema import PredictRequest, PredictResponse, ErrorResponse
from model_loader import ModelLoader

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# グローバル変数
model_loader = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションライフサイクル管理
    """
    global model_loader
    
    # 起動時処理
    logger.info("Starting Real Estate Appraisal API...")
    
    try:
        # モデル読み込み
        model_loader = ModelLoader()
        logger.info("Model loaded successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # 終了時処理
    logger.info("Shutting down Real Estate Appraisal API...")


# FastAPIアプリケーション作成
app = FastAPI(
    title="Real Estate Appraisal API",
    description="不動産価格予測API - 東京23区対応",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定 - 環境変数から読み込み
# 開発環境ではlocalhostを許可、本番環境では特定のドメインのみ許可
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # 環境変数で制御
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # 必要なメソッドのみ許可
    allow_headers=["Content-Type", "Authorization"],  # 必要なヘッダーのみ
)


@app.get("/")
async def root():
    """
    ルートエンドポイント
    """
    return {
        "message": "Real Estate Appraisal API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    global model_loader
    
    if model_loader is None or not model_loader.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_info": model_loader.get_model_info()
    }


@app.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        200: {"model": PredictResponse, "description": "Successful prediction"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def predict_price(request: PredictRequest):
    """
    不動産価格予測エンドポイント
    
    Args:
        request: 予測リクエストデータ
        
    Returns:
        PredictResponse: 予測結果
    """
    global model_loader
    
    # モデル読み込み確認
    if model_loader is None or not model_loader.is_loaded():
        logger.error("Model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    try:
        # リクエストデータを辞書に変換
        request_data = request.dict()
        
        logger.info(f"Prediction request: {request_data}")
        
        # 予測実行
        result = model_loader.predict(request_data)
        
        # レスポンス作成
        response = PredictResponse(
            predicted_price=result['predicted_price'],
            confidence=result.get('confidence'),
            features_used=result.get('features_used')
        )
        
        logger.info(f"Prediction successful: {result['predicted_price']:.1f}万円")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid input data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Prediction service error: {str(e)}"
        )


@app.post("/predict/batch")
async def predict_batch(requests: list[PredictRequest]):
    """
    バッチ予測エンドポイント（複数物件の一括予測）
    
    Args:
        requests: 予測リクエストのリスト
        
    Returns:
        List[PredictResponse]: 予測結果のリスト
    """
    global model_loader
    
    if model_loader is None or not model_loader.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    if len(requests) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many requests. Maximum 100 requests per batch."
        )
    
    results = []
    errors = []
    
    for i, request in enumerate(requests):
        try:
            request_data = request.dict()
            result = model_loader.predict(request_data)
            
            response = PredictResponse(
                predicted_price=result['predicted_price'],
                confidence=result.get('confidence'),
                features_used=result.get('features_used')
            )
            results.append(response)
            
        except Exception as e:
            error_response = {
                "index": i,
                "error": str(e),
                "input": request.dict()
            }
            errors.append(error_response)
            results.append(None)
    
    return {
        "results": results,
        "errors": errors,
        "total_processed": len(requests),
        "successful": len([r for r in results if r is not None]),
        "failed": len(errors)
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    グローバル例外ハンドラー
    """
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


# Lambda handler for AWS Lambda deployment
handler = Mangum(app)

if __name__ == "__main__":
    # 開発サーバー起動
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )