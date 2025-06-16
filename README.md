# 🏗 Real Estate Appraisal App

不動産査定アプリケーション - Django (UI) + FastAPI (ML API) によるマイクロサービス構成

## 🎯 概要

重回帰分析モデルを使用した不動産査定システム。ローカル開発とAWS本番環境に対応。

### 技術構成
- **Django**: フロントエンドUI（フォーム入力、査定結果表示）
- **FastAPI**: 査定API（MLモデルによる推論処理）
- **機械学習**: 重回帰分析モデル
- **ローカル環境**: 独立Dockerコンテナ（個別実行）
- **本番環境**: ECR → ECS Fargate + ALB (CloudFormation管理)

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

### ローカル
```
Django (8080) ──HTTP──→ FastAPI (8000)
```

### 本番 (AWS) - 削除済み
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

### AWS環境（過去運用時）
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