"""
ヘルスチェックエンドポイントのルーター
"""

import logging
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Request

from model_loader import ModelLoader

# ロガー設定
logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> Dict[str, str]:
    """
    ルートエンドポイント
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[request_id={request_id}] Root endpoint accessed")
    
    return {
        "message": "Real Estate Appraisal API",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """
    ヘルスチェックエンドポイント
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[request_id={request_id}] Health check requested")
    
    # 依存性注入：app.stateからModelLoaderを取得
    model_loader: ModelLoader = request.app.state.model_loader
    
    if not model_loader.is_loaded():
        logger.error(f"[request_id={request_id}] Health check failed: Model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    model_info = model_loader.get_model_info()
    logger.info(f"[request_id={request_id}] Health check successful")
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_info": model_info
    }