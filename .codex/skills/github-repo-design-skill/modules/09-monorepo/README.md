# Monorepo 结构

## 推荐结构

```
monorepo/
├── .github/
│   └── workflows/
├── packages/
│   ├── core/
│   │   ├── src/
│   │   ├── package.json
│   │   └── README.md
│   ├── cli/
│   │   ├── src/
│   │   ├── package.json
│   │   └── README.md
│   └── web/
│       ├── src/
│       ├── package.json
│       └── README.md
├── docs/
├── examples/
├── scripts/
├── package.json          # 根 package.json
├── pnpm-workspace.yaml   # 或 lerna.json
├── turbo.json            # Turborepo 配置
└── README.md
```

## 工具选择

| 工具 | 特点 |
|------|------|
| **pnpm workspaces** | 高效磁盘空间，原生支持 |
| **Turborepo** | 增量构建，远程缓存 |
| **Nx** | 功能丰富，适合大型项目 |
| **Lerna** | 经典方案，版本管理 |

## pnpm workspace 配置

文件位置: `pnpm-workspace.yaml`

```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

## Turborepo 配置

文件位置: `turbo.json`

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## Monorepo CI 配置

```yaml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm turbo build test lint
```

## 版本管理

### Changesets
```bash
# 安装
pnpm add -Dw @changesets/cli

# 初始化
pnpm changeset init

# 添加变更
pnpm changeset

# 发布
pnpm changeset version
pnpm changeset publish
```
