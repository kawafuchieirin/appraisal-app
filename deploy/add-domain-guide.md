# ドメイン設定ガイド

## 現在の状況
- ALB URL: http://satei-app-debug-alb-828969271.ap-northeast-1.elb.amazonaws.com
- HTTPSなし、カスタムドメインなし

## オプション

### オプション1: 既存ドメインを使用
```bash
# 1. Route 53でホストゾーンを作成
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)

# 2. ALBにドメインを向ける
aws route53 change-resource-record-sets --hosted-zone-id Z123456 \
  --change-batch file://route53-record.json
```

### オプション2: CloudFront経由（無料・HTTPS対応）
```bash
# CloudFrontディストリビューションを作成
aws cloudformation create-stack \
  --stack-name satei-app-cloudfront \
  --template-body file://cloudfront-template.yaml \
  --parameters ParameterKey=ALBDNSName,ParameterValue=satei-app-debug-alb-828969271.ap-northeast-1.elb.amazonaws.com
```

### オプション3: Route 53でドメイン購入
```bash
# ドメインの可用性を確認
aws route53domains check-domain-availability --domain-name satei-app.com

# ドメインを登録（有料）
aws route53domains register-domain --domain-name satei-app.com \
  --duration-in-years 1 --admin-contact file://contact.json
```

## Django設定の更新

ドメイン設定後、以下の環境変数を更新する必要があります：

```yaml
Environment:
  - Name: ALLOWED_HOSTS
    Value: 'your-domain.com,www.your-domain.com,localhost'
  - Name: CSRF_TRUSTED_ORIGINS
    Value: 'https://your-domain.com,https://www.your-domain.com'
```

## 推奨: CloudFront経由のHTTPS化

メリット：
- 無料でHTTPS化
- グローバルCDN
- DDoS保護
- キャッシュによる高速化

デメリット：
- *.cloudfront.netドメイン（カスタムドメインも可能）
- 設定がやや複雑