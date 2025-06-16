# デプロイメント

このディレクトリには、ローカル開発環境と AWS 本番環境のデプロイメント設定が含まれています。

## 📁 ディレクトリ構成

```
deploy/
├── README.md           # このファイル
├── local/              # ローカル開発環境
│   ├── docker-compose.yml
│   ├── start.sh
│   ├── stop.sh
│   ├── test.sh
│   └── README.md
└── aws/                # AWS本番環境
    ├── Dockerfile
    ├── push_to_ecr.sh
    ├── deploy_lambda.sh
    └── README.md
```

## 🚀 クイックスタート

### ローカル開発環境

```bash
# 環境起動
./deploy/local/start.sh

# テスト実行
./deploy/local/test.sh

# 環境停止
./deploy/local/stop.sh
```

**アクセス先:**
- Django UI: http://localhost:8080
- FastAPI: http://localhost:8000

### AWS本番環境

```bash
# 1. ECRにプッシュ
./deploy/aws/push_to_ecr.sh

# 2. Lambda + API Gateway デプロイ
./deploy/aws/deploy_lambda.sh
```

## 📊 アーキテクチャ

### ローカル環境
```
┌─────────────┐    HTTP     ┌─────────────┐
│   Django    │ ──────────→ │   FastAPI   │
│ (Port 8080) │             │ (Port 8000) │
└─────────────┘             └─────────────┘
       │                           │
       └────── Docker Network ──────┘
```

### AWS本番環境
```
┌─────────────┐    HTTPS    ┌──────────────────┐
│   Django    │ ──────────→ │  API Gateway     │
│   (Local)   │             │       │          │
└─────────────┘             │       ▼          │
                            │   Lambda         │
                            │  (FastAPI)       │
                            └──────────────────┘
```

## 🔧 前提条件

### ローカル開発
- Docker & Docker Compose
- 8000, 8080 ポートが利用可能

### AWS本番環境
- AWS CLI 設定済み
- ECR, Lambda, API Gateway権限
- IAM ロール: `lambda-execution-role`

## 📖 詳細情報

- **ローカル環境**: [local/README.md](local/README.md)
- **AWS環境**: [aws/README.md](aws/README.md)