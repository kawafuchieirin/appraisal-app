# 🏗 Real Estate Appraisal App

不動産査定アプリケーション - Django (UI) + FastAPI (ML API) による単一コンテナ構成

## 🎯 概要

重回帰分析モデルを使用した不動産査定システム。ローカルと本番環境で統一的なDocker構成を採用。

### 技術構成
- **Django**: フロントエンドUI（フォーム入力、査定結果表示）
- **FastAPI**: 査定API（MLモデルによる推論処理）
- **機械学習**: 重回帰分析モデル
- **ローカル環境**: 単一Dockerコンテナ（個別実行）
- **本番環境**: ECR → Lambda + API Gateway

## 🗂️ ディレクトリ構成

```
appraisal-app/
├── django_app/       # Django アプリ本体
├── fastapi_app/      # FastAPI による査定API（Lambda対応）
├── model_create/     # MLモデル作成・保存
└── deploy/           # デプロイメント・設定ファイル
    ├── lambda/       # Lambda用デプロイスクリプト
    ├── .env.development  # 開発環境設定
    ├── .env.production   # 本番環境設定
    ├── run_dev.sh    # 開発環境（両サービス起動）
    ├── run_django.sh # Django単体実行
    ├── run_fastapi.sh# FastAPI単体実行
    └── push_to_ecr.sh# ECRデプロイスクリプト
```

## 🛠 開発環境

### 統合開発環境（推奨）
```bash
# 両サービスを同時起動
./deploy/run_dev.sh

# アクセス
# Django: http://localhost:8080
# FastAPI: http://localhost:8000
```

### 個別サービス実行
```bash
# FastAPI のみ
./deploy/run_fastapi.sh [port] [environment]

# Django のみ
./deploy/run_django.sh [port] [environment]
```

### モデル学習
```bash
python model_create/train_model.py
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