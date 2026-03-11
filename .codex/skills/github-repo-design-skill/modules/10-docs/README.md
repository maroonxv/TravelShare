# 文档网站集成

## 推荐工具

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| **Docusaurus** | React 驱动，功能丰富 | 大型项目文档 |
| **VitePress** | Vue 驱动，轻量快速 | Vue 生态项目 |
| **MkDocs** | Python 驱动，Material 主题 | Python 项目 |
| **GitBook** | 在线编辑，协作友好 | 团队文档 |
| **Nextra** | Next.js 驱动 | Next.js 项目 |

## GitHub Pages 部署

文件位置: `.github/workflows/docs.yml`

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci && npm run docs:build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist
      - uses: actions/deploy-pages@v4
        id: deployment
```

## VitePress 快速开始

```bash
# 安装
npm add -D vitepress

# 初始化
npx vitepress init

# 开发
npx vitepress dev docs

# 构建
npx vitepress build docs
```

## Docusaurus 快速开始

```bash
# 创建项目
npx create-docusaurus@latest docs classic

# 开发
cd docs && npm start

# 构建
npm run build
```

## MkDocs 快速开始

```bash
# 安装
pip install mkdocs-material

# 创建项目
mkdocs new docs

# 开发
mkdocs serve

# 构建
mkdocs build
```

## 文档结构建议

```
docs/
├── index.md              # 首页
├── getting-started/      # 快速开始
│   ├── installation.md
│   └── quick-start.md
├── guide/                # 指南
│   ├── basics.md
│   └── advanced.md
├── api/                  # API 文档
│   └── reference.md
└── examples/             # 示例
    └── basic.md
```
