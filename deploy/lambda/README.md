# AWS Lambda + API Gateway デプロイガイド

## 📋 概要

このディレクトリには、FastAPI査定アプリをAWS Lambda + API Gatewayにデプロイするためのファイルが含まれています。

## 🚀 デプロイ手順

### 1. 前提条件

- AWS CLI がインストール・設定済み
- Docker がインストール済み
- 適切なIAM権限（ECR、Lambda、API Gateway、IAM）

### 2. IAM ロール作成

```bash
# Lambda実行ロール作成
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# 基本実行ポリシー付与
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 3. ECRにプッシュ

```bash
# ECRリポジトリ作成とイメージプッシュ
./deploy/push_to_ecr.sh ap-northeast-1 satei-api
```

### 4. Lambda + API Gateway デプロイ

```bash
# Lambda関数とAPI Gateway作成
./deploy/deploy_lambda.sh ap-northeast-1 satei-api
```

## 📁 ファイル構成

```
deploy/
├── README.md              # このファイル
├── push_to_ecr.sh         # ECRプッシュスクリプト
└── deploy_lambda.sh       # Lambda+API Gatewayデプロイスクリプト

# プロジェクトルート
├── Dockerfile             # Lambda用プロダクション Dockerfile
├── Dockerfile.dev         # 開発用 FastAPI Dockerfile
├── docker-compose.yml     # ローカル開発用
└── django_app/
    └── Dockerfile.dev     # 開発用 Django Dockerfile
```

## 🔧 設定

### 環境変数

Lambda関数には以下の環境変数が自動設定されます：

- `USE_MODEL_API=true`
- `AWS_LWA_PORT=8000`
- `AWS_LWA_READINESS_CHECK_PATH=/health`

### Django側設定

デプロイ後、Django の `.env` ファイルを更新：

```bash
# Django .env
USE_MODEL_API=true
FASTAPI_URL=https://YOUR_API_ID.execute-api.ap-northeast-1.amazonaws.com
FASTAPI_TIMEOUT=30
```

## 🧪 テスト

### ヘルスチェック

```bash
curl https://YOUR_API_ID.execute-api.ap-northeast-1.amazonaws.com/health
```

### 予測テスト

```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-northeast-1.amazonaws.com/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "building_area": 80,
    "land_area": 120,
    "building_age": 10,
    "ward_name": "世田谷区",
    "year": 2024,
    "quarter": 1
  }'
```

## 📊 モニタリング

### CloudWatch ログ

```bash
# Lambda ログ確認
aws logs tail /aws/lambda/satei-api --follow
```

### メトリクス

- Lambda実行時間
- API Gateway リクエスト数
- エラー率

## 🔄 更新手順

1. コード変更
2. ECR再プッシュ: `./deploy/push_to_ecr.sh`
3. Lambda更新: `./deploy/deploy_lambda.sh`

## ⚠️ 注意事項

- Lambda の最大実行時間: 15分
- メモリ制限: 10GB（現在1GB設定）
- ECRイメージサイズ制限: 10GB
- MLモデルファイルはDockerイメージに含まれます

## 🚨 トラブルシューティング

### よくある問題

1. **Lambda関数作成失敗**
   - IAMロールの権限確認
   - ECRイメージが存在するか確認

2. **API Gateway接続エラー**
   - CORS設定確認
   - Lambda権限確認

3. **モデル読み込み失敗**
   - Dockerイメージにモデルファイルが含まれているか確認
   - パスが正しいか確認

### ログ確認

```bash
# CloudWatch ログストリーム一覧
aws logs describe-log-streams \
  --log-group-name /aws/lambda/satei-api \
  --order-by LastEventTime \
  --descending \
  --max-items 1

# 最新ログ確認
aws logs get-log-events \
  --log-group-name /aws/lambda/satei-api \
  --log-stream-name [LOG_STREAM_NAME]
```