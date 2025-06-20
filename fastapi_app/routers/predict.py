"""
予測エンドポイントのルーター
"""

import logging
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status, Request

from predict_schema import PredictRequest, PredictResponse, ErrorResponse
from model_types import BatchPredictResponse, ErrorDetail, PredictResult
from model_loader import ModelLoader

# ロガー設定
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post(
    "",
    response_model=PredictResponse,
    responses={
        200: {"model": PredictResponse, "description": "Successful prediction"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def predict_price(request: Request, predict_request: PredictRequest) -> PredictResponse:
    """
    不動産価格予測エンドポイント
    
    Args:
        request: FastAPIリクエストオブジェクト
        predict_request: 予測リクエストデータ
        
    Returns:
        PredictResponse: 予測結果
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[request_id={request_id}] Prediction request started")
    
    # 依存性注入：app.stateからModelLoaderを取得
    model_loader: ModelLoader = request.app.state.model_loader
    
    # モデル読み込み確認
    if not model_loader.is_loaded():
        logger.error(f"[request_id={request_id}] Model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    try:
        # リクエストデータを辞書に変換
        request_data = predict_request.dict()
        
        logger.info(f"[request_id={request_id}] Processing prediction: {request_data}")
        
        # 予測実行（型安全な戻り値）
        result: PredictResult = model_loader.predict(request_data)
        
        # レスポンス作成
        response = PredictResponse(
            predicted_price=result['predicted_price'],
            confidence=result.get('confidence'),
            features_used=result.get('features_used')
        )
        
        logger.info(f"[request_id={request_id}] Prediction successful: {result['predicted_price']:.1f}万円")
        
        return response
        
    except ValueError as e:
        logger.warning(f"[request_id={request_id}] Invalid input data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"[request_id={request_id}] Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Prediction service error: {str(e)}"
        )


@router.post("/batch", response_model=BatchPredictResponse)
async def predict_batch(request: Request, requests: List[PredictRequest]) -> BatchPredictResponse:
    """
    バッチ予測エンドポイント（複数物件の一括予測）
    
    Args:
        request: FastAPIリクエストオブジェクト
        requests: 予測リクエストのリスト
        
    Returns:
        BatchPredictResponse: バッチ予測結果
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[request_id={request_id}] Batch prediction started with {len(requests)} items")
    
    # 依存性注入：app.stateからModelLoaderを取得
    model_loader: ModelLoader = request.app.state.model_loader
    
    if not model_loader.is_loaded():
        logger.error(f"[request_id={request_id}] Model not loaded for batch prediction")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not available"
        )
    
    if len(requests) > 100:
        logger.warning(f"[request_id={request_id}] Too many requests: {len(requests)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many requests. Maximum 100 requests per batch."
        )
    
    results: List[PredictResponse | None] = []
    errors: List[ErrorDetail] = []
    
    for i, predict_request in enumerate(requests):
        try:
            request_data = predict_request.dict()
            result: PredictResult = model_loader.predict(request_data)
            
            response = PredictResponse(
                predicted_price=result['predicted_price'],
                confidence=result.get('confidence'),
                features_used=result.get('features_used')
            )
            results.append(response)
            
        except Exception as e:
            error_detail: ErrorDetail = {
                "index": i,
                "error": str(e),
                "input": predict_request.dict()
            }
            errors.append(error_detail)
            results.append(None)
            
            logger.warning(f"[request_id={request_id}] Batch item {i} failed: {e}")
    
    successful_count = len([r for r in results if r is not None])
    logger.info(f"[request_id={request_id}] Batch prediction completed: {successful_count}/{len(requests)} successful")
    
    return BatchPredictResponse(
        results=results,
        errors=errors,
        total_processed=len(requests),
        successful=successful_count,
        failed=len(errors)
    )