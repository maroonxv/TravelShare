# 安全最佳实践

## 依赖安全

文件位置: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## 安全扫描工作流

文件位置: `.github/workflows/security.yml`

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行

jobs:
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript, python
      - uses: github/codeql-action/analyze@v3

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
```

## 密钥扫描

文件位置: `.github/workflows/secrets.yml`

```yaml
name: Secret Scan

on: [push, pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

## 安全检查清单

- [ ] 启用了 Dependabot
- [ ] 配置了 CodeQL 扫描
- [ ] 添加了 SECURITY.md
- [ ] 无硬编码密钥
- [ ] 启用了分支保护
- [ ] 要求 PR 审查

## SECURITY.md 模板

```markdown
# 安全策略

## 支持的版本

| 版本 | 支持状态 |
|------|----------|
| 2.x  | ✅ 支持  |
| 1.x  | ❌ 不再支持 |

## 报告漏洞

如果发现安全漏洞，请：

1. **不要**公开创建 Issue
2. 发送邮件至 security@example.com
3. 包含漏洞详细描述和复现步骤

我们会在 48 小时内回复。
```

## 安全工具推荐

| 工具 | 用途 |
|------|------|
| **Dependabot** | 依赖更新 |
| **CodeQL** | 代码扫描 |
| **TruffleHog** | 密钥扫描 |
| **Snyk** | 漏洞扫描 |
| **OSSF Scorecard** | 安全评分 |
