# AWS Resources Cleanup Guide

このガイドでは、Real Estate Appraisal Applicationで作成されたAWSリソースを安全に削除する方法を説明します。

## 📋 削除対象リソース

### CloudFormationで管理されるリソース
- **VPC とネットワーク**: VPC、サブネット、インターネットゲートウェイ、ルートテーブル
- **Application Load Balancer**: ALB、ターゲットグループ、リスナー
- **ECS**: クラスター、サービス、タスク定義
- **Security Groups**: ALB用、ECS用セキュリティグループ
- **CloudWatch**: ロググループ

### 個別で管理されるリソース
- **ECR Repositories**: satei-django、satei-fastapi
- **Container Images**: ECR内の全てのDockerイメージ

## 🚀 削除方法

### 方法1: 自動削除スクリプト（推奨）

```bash
# 基本的な削除（ap-northeast-1リージョン）
./deploy/cleanup_aws_resources.sh

# 他のリージョンを指定
./deploy/cleanup_aws_resources.sh us-west-2

# ヘルプを表示
./deploy/cleanup_aws_resources.sh --help
```

#### スクリプトの機能
- ✅ 削除前の確認プロンプト
- ✅ AWS CLI設定チェック
- ✅ CloudFormationスタックの削除
- ✅ ECRリポジトリとイメージの削除
- ✅ 孤立リソースのチェック
- ✅ 削除結果のサマリー表示

### 方法2: 個別リソース削除（トラブル時）

CloudFormationスタックの削除が失敗した場合に使用：

```bash
# Python3が必要
python3 deploy/cleanup_individual_resources.py

# 他のリージョンを指定
python3 deploy/cleanup_individual_resources.py us-west-2

# ヘルプを表示
python3 deploy/cleanup_individual_resources.py --help
```

#### 個別削除の機能
- 🔧 ECSサービスの強制停止・削除
- 🔧 ALBとターゲットグループの削除
- 🔧 CloudFormationスタックの削除
- 🔧 ECRリポジトリの削除
- 🔧 CloudWatchログの削除

### 方法3: 手動削除（コンソール経由）

AWS Management Consoleから手動で削除：

1. **CloudFormation**
   ```
   https://console.aws.amazon.com/cloudformation/
   → "satei-app-v2" スタックを選択 → 削除
   ```

2. **ECR**
   ```
   https://console.aws.amazon.com/ecr/
   → "satei-django", "satei-fastapi" リポジトリを削除
   ```

## ⚠️ 注意事項

### 削除前の確認事項
- [ ] **データのバックアップ**: 必要なデータは事前にバックアップ
- [ ] **他のリソースへの影響**: 共有VPCや他のアプリケーションとの依存関係を確認
- [ ] **課金の確認**: 削除後に予期しない課金が発生しないことを確認

### 削除順序の重要性
1. **ECSサービス** → タスクの停止
2. **ALB/ターゲットグループ** → ネットワーク接続の切断
3. **CloudFormationスタック** → その他リソースの削除
4. **ECRリポジトリ** → コンテナイメージの削除

### 削除できない場合のトラブルシューティング

#### CloudFormation削除失敗
```bash
# 依存関係エラーの場合
aws cloudformation describe-stack-events --stack-name satei-app-v2 --region ap-northeast-1

# 強制削除（注意深く実行）
python3 deploy/cleanup_individual_resources.py
```

#### ECSサービス削除失敗
```bash
# サービスを0に スケールダウン
aws ecs update-service --cluster satei-app-v2-cluster --service satei-app-v2-django-service --desired-count 0 --region ap-northeast-1

# タスクの停止を待ってからサービス削除
aws ecs delete-service --cluster satei-app-v2-cluster --service satei-app-v2-django-service --region ap-northeast-1
```

#### ECR削除失敗
```bash
# 全イメージを削除してからリポジトリ削除
aws ecr batch-delete-image --repository-name satei-django --image-ids imageTag=latest --region ap-northeast-1
aws ecr delete-repository --repository-name satei-django --force --region ap-northeast-1
```

## 💰 コスト確認

削除後は以下を確認してください：

### 即座に停止する課金
- ECS Fargate実行時間
- Application Load Balancer時間
- ECR ストレージ

### 継続する可能性のある課金
- CloudWatch Logs（保持期間中）
- NAT Gateway（VPC内に残っている場合）
- Elastic IP（解放されていない場合）

### 課金確認コマンド
```bash
# 現在の課金状況を確認
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-12-31 --granularity MONTHLY --metrics BlendedCost

# 特定サービスの利用状況
aws ce get-dimension-values --dimension SERVICE --time-period Start=2024-01-01,End=2024-12-31
```

## 🔍 削除確認

削除完了後、以下のコンソールで確認：

- [CloudFormation](https://console.aws.amazon.com/cloudformation/)
- [ECR](https://console.aws.amazon.com/ecr/)
- [ECS](https://console.aws.amazon.com/ecs/)
- [EC2 (Load Balancers)](https://console.aws.amazon.com/ec2/)
- [VPC](https://console.aws.amazon.com/vpc/)
- [CloudWatch](https://console.aws.amazon.com/cloudwatch/)

## 📞 サポート

削除で問題が発生した場合：

1. **エラーメッセージを確認**: CloudFormationイベントやAWS CLIのエラー出力
2. **依存関係を確認**: リソース間の依存関係が削除を阻んでいないか
3. **個別削除を試行**: `cleanup_individual_resources.py`を使用
4. **AWSサポートに問い合わせ**: 技術的な問題の場合

---

⚠️ **重要**: リソース削除は取り消しできません。実行前に必ず内容を確認してください。