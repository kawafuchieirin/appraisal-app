# 🏗 Real Estate Appraisal App

不動産査定アプリケーション - Django (UI) + FastAPI (ML API) による多コンテナ構成

## 🎯 概要

重回帰分析モデルを使用した不動産査定システム。ローカルと本番環境で統一的なDocker構成を採用。

### 技術構成
- **Django**: フロントエンドUI（フォーム入力、査定結果表示）
- **FastAPI**: 査定API（MLモデルによる推論処理）
- **機械学習**: 重回帰分析モデル
- **ローカル環境**: docker-compose マルチコンテナ
- **本番環境**: FastAPI → ECR → Lambda + API Gateway

## 🗂️ ディレクトリ構成

```
app/
├── main_app/         # Django アプリ本体
├── ssessment/        # FastAPI による査定API（Lambda対応）
├── model_create/     # MLモデル作成・保存
├── deploy/           
│   ├── local/        # docker-compose 環境
│   └── lambda/       # Lambda用 Dockerfile・デプロイスクリプト
```

## 🚀 開発タスク

1. **モデル作成**: 重回帰モデルの学習と保存
2. **査定API**: FastAPI による `/predict` エンドポイント実装
3. **Django UI**: ユーザー入力フォーム → API呼び出し → 結果表示
4. **ローカル環境**: docker-compose による統合環境構築
5. **Lambda対応**: FastAPI の Lambda 化と ECR デプロイ

## 🛠 開発開始

```bash
# ローカル開発環境起動
docker-compose -f deploy/local/docker-compose.yml up

# モデル学習
python model_create/train_model.py

# API テスト
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"features": [...]}'
```

## 📋 デプロイ構成

### ローカル
```
Django ──HTTP──→ FastAPI
```

### 本番 (AWS)
```
Django ──HTTP──→ API Gateway → Lambda (ECR上のFastAPI)
```