# README.md 设计指南

## README 必备内容

```markdown
# 项目名称

简短的一句话描述项目用途。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)

## 功能特性

- 特性 1：简要说明
- 特性 2：简要说明
- 特性 3：简要说明

## 快速开始

### 安装

\`\`\`bash
npm install package-name
# 或
pip install package-name
\`\`\`

### 基本用法

\`\`\`javascript
import { feature } from 'package-name';

// 示例代码
const result = feature();
\`\`\`

## 文档

详细文档请访问 [文档链接](docs/)

## 贡献

欢迎贡献！请阅读 [贡献指南](CONTRIBUTING.md)

## 许可证

本项目采用 [MIT 许可证](LICENSE)
```

## README 设计原则

| 原则 | 说明 |
|------|------|
| **简洁明了** | 开头一句话说明项目用途 |
| **快速上手** | 提供安装和基本用法示例 |
| **视觉吸引** | 使用徽章、截图、GIF 演示 |
| **结构清晰** | 使用标题层级组织内容 |
| **链接完整** | 提供文档、贡献指南等链接 |

## README 设计模式

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| **极简型** | 小型工具库 | 一屏内展示核心信息 |
| **文档型** | 框架/SDK | 详细 API 和示例 |
| **展示型** | UI 组件库 | 大量截图和演示 |
| **教程型** | 学习项目 | 步骤式指南 |

## 优秀案例

### React (facebook/react)
- 简洁的项目描述
- 清晰的文档链接
- 多种安装方式
- 贡献指南链接

### Vue.js (vuejs/core)
- 徽章展示构建状态
- 快速开始指南
- 生态系统链接
- 赞助商展示

### TensorFlow (tensorflow/tensorflow)
- 详细的安装说明
- 多平台支持说明
- 丰富的示例代码
- 社区资源链接
