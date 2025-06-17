# 🏗 Real Estate Appraisal App

不動産査定アプリケーション - Django (UI) + FastAPI (ML API) によるマイクロサービス構成

## 🎯 概要

Ridge回帰モデルを使用した東京23区の不動産価格査定システム。ローカル開発環境で動作し、AWS環境へのデプロイも可能。

### 技術構成
- **Django**: フロントエンドUI（フォーム入力、査定結果表示）
- **FastAPI**: 査定API（MLモデルによる推論処理）
- **機械学習**: Ridge回帰モデル（StandardScaler + 9次元特徴量）
- **ローカル環境**: 独立Dockerコンテナ（個別実行）
- **本番環境**: AWS ECS Fargate + ALB (CloudFormation管理)

## 🗂️ ディレクトリ構成

```
appraisal-app/
├── django_app/       # Django アプリ本体
│   ├── Dockerfile.dev # 開発用Dockerfile
│   └── Dockerfile.ecs # ECS用Dockerfile
├── fastapi_app/      # FastAPI による査定API（ECS対応）
│   ├── Dockerfile.dev # 開発用Dockerfile
│   └── Dockerfile.ecs # ECS用Dockerfile
├── model_create/     # MLモデル作成・保存
└── deploy/           # デプロイメント・設定ファイル
    ├── cloudformation-template.yaml # AWSインフラ定義
    ├── django-ecs-task-definition.json # Django ECS設定
    ├── fastapi-ecs-task-definition.json # FastAPI ECS設定
    ├── cleanup_aws_resources.sh # AWSリソース削除
    ├── cleanup_individual_resources.py # 個別リソース削除
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

# 統合テスト実行
python django_app/test_integration.py
python fastapi_app/test_api.py
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
# モデル訓練とファイル生成
cd model_create
python train_model.py

# テストデータ生成
python create_sample_data.py
```

## 📋 アーキテクチャ詳細

### ローカル環境
```
Django (8080) ──HTTP──→ FastAPI (8000)
```

### 本番環境 (AWS)
```
ALB ──→ Django (ECS) ──HTTP──→ FastAPI (ECS)
     └─→ FastAPI (ECS)

構成要素:
- CloudFormation: インフラ管理
- ECS Fargate: コンテナ実行
- Application Load Balancer: 負荷分散
- ECR: コンテナイメージ保存
- VPC: ネットワーク分離
```

## 🔧 AWS運用

### デプロイ
```bash
# ECRにイメージをプッシュ
./deploy/push_to_ecr.sh ap-northeast-1 all

# CloudFormationでインフラ構築
aws cloudformation deploy \
  --template-file deploy/cloudformation-template.yaml \
  --stack-name satei-app-v2 \
  --capabilities CAPABILITY_IAM

# ECSサービスの更新
aws ecs update-service --cluster satei-app-v2-cluster \
  --service satei-app-v2-django-service --force-new-deployment
```

### リソース削除
```bash
# 自動削除（推奨）
./deploy/cleanup_aws_resources.sh

# 個別削除（トラブル時）
python3 deploy/cleanup_individual_resources.py

# 手動確認
aws cloudformation list-stacks --query "StackSummaries[?contains(StackName, 'satei')]"
aws ecr describe-repositories --query "repositories[?contains(repositoryName, 'satei')]"
```

## 🔍 トラブルシューティング

### 開発環境
```bash
# サービス状況確認
docker ps
curl http://localhost:8000/health
curl http://localhost:8080

# ログ確認
docker logs <container_id>
```

### AWS環境
```bash
# ECSサービス状況
aws ecs describe-services --cluster satei-app-v2-cluster \
  --services satei-app-v2-django-service satei-app-v2-fastapi-service

# ALBヘルスチェック
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# CloudWatchログ
aws logs filter-log-events --log-group-name /ecs/satei-app \
  --start-time $(date -d '10 minutes ago' +%s)000
```

## 🏗️ 査定処理フロー

### 1. 入力項目
- **建物面積**: 10-1000㎡
- **土地面積**: 10-2000㎡
- **築年数**: 0-50年
- **区名**: 東京23区から選択
- **査定年**: 2024年（固定）
- **査定時期**: 四半期（1-4）

### 2. 処理フロー
```
ユーザー入力 → Django検証 → FastAPI推論 → 結果表示
```

### 3. 機械学習モデル
- **アルゴリズム**: Ridge回帰
- **特徴量**: 9次元（面積、築年数、地域、時期など）
- **出力**: 予測価格（万円）+ 信頼度（%）

## 📊 使用例

### APIリクエスト例
```json
{
  "building_area": 80.0,
  "land_area": 120.0,
  "building_age": 5,
  "ward_name": "世田谷区",
  "year": 2024,
  "quarter": 2
}
```

### レスポンス例
```json
{
  "predicted_price": 5642.0,
  "confidence": 86.7,
  "features_used": {
    "building_area": 80.0,
    "land_area": 120.0,
    "building_age": 5.0,
    "ward_世田谷区": 1.0
  }
}
```