# 仓库设置优化

## 1. Topics (主题标签)

添加相关主题提高可发现性：
- 技术栈：`javascript`, `python`, `react`
- 类型：`cli`, `library`, `framework`
- 领域：`machine-learning`, `web`, `devops`

### 推荐 Topics 数量
- 最少：3 个
- 推荐：5-10 个
- 最多：20 个

## 2. 社交预览图

- 尺寸：1280 x 640 像素
- 格式：PNG, JPG, GIF
- 大小：< 1 MB

### 设计建议
- 包含项目名称和 Logo
- 使用品牌色彩
- 简洁清晰的设计
- 可使用 Canva、Figma 等工具

## 3. 分支保护规则

推荐为 `main` 分支启用：
- ✅ 要求 PR 审查
- ✅ 要求状态检查通过
- ✅ 要求线性历史
- ✅ 禁止强制推送

### 配置路径
Settings → Branches → Add branch protection rule

### 推荐配置
```
Branch name pattern: main

☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale pull request approvals when new commits are pushed

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  Status checks: CI

☑ Require linear history

☑ Do not allow bypassing the above settings
```

## 4. 仓库功能设置

### 推荐启用
- ✅ Issues
- ✅ Discussions（社区项目）
- ✅ Projects（项目管理）
- ✅ Wiki（可选）

### 推荐禁用
- ❌ Wiki（如果使用外部文档）
- ❌ Projects（如果使用外部工具）

## 5. 安全设置

### 推荐启用
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Code scanning alerts
- ✅ Secret scanning alerts

### 配置路径
Settings → Security → Code security and analysis
