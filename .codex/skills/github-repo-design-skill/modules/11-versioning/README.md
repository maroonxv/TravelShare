# 版本管理策略

## 语义化版本 (SemVer)

```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的 API 变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的问题修复
```

## 预发布版本

```
1.0.0-alpha.1
1.0.0-beta.1
1.0.0-rc.1
1.0.0
```

## Conventional Commits

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
perf: 性能优化
test: 测试
chore: 构建/工具
```

### 示例
```
feat(auth): add OAuth2 support
fix(api): handle null response
docs: update installation guide
chore(deps): bump lodash to 4.17.21
```

## 自动版本管理

### semantic-release

文件位置: `.releaserc.json`

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github"
  ]
}
```

### 工作流配置

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## CHANGELOG.md 格式

```markdown
# Changelog

## [2.0.0] - 2024-01-15

### Breaking Changes
- 移除了废弃的 API

### Added
- 新增功能 A
- 新增功能 B

### Fixed
- 修复了 bug #123

### Changed
- 优化了性能

## [1.0.0] - 2023-12-01

### Added
- 初始发布
```

## Releases 最佳实践

1. 使用语义化版本：`MAJOR.MINOR.PATCH`
2. 编写清晰的发布说明
3. 包含变更日志链接
4. 标记重大变更 (Breaking Changes)
