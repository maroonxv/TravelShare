---
name: github-repo-design
description: GitHub 仓库设计与 README 最佳实践指南，帮助创建专业的开源项目结构
triggers:
  - github repo
  - repository design
  - readme design
  - 仓库设计
  - 项目结构
  - 开源项目
  - profile readme
  - github profile
  - readme badge
  - readme template
---

# GitHub 仓库设计与 README 最佳实践

> 基于 100+ 优秀开源项目研究总结的最佳实践指南

## 使用场景

当用户需要以下帮助时使用此 skill：
- 创建新的 GitHub 仓库
- 设计项目文件结构
- 编写 README 文件
- 配置开源项目必备文件
- 优化仓库可发现性
- 设置 GitHub Profile README

---

## 模块索引

本 skill 采用分包分级架构，按主题组织为独立模块：

### 基础模块

| 模块 | 说明 | 路径 |
|------|------|------|
| **01-structure** | 仓库核心文件结构 | `modules/01-structure/` |
| **02-readme** | README 设计指南 | `modules/02-readme/` |
| **03-config** | 核心配置文件 | `modules/03-config/` |
| **04-templates** | Issue/PR 模板 | `modules/04-templates/` |
| **05-settings** | 仓库设置优化 | `modules/05-settings/` |

### 进阶模块

| 模块 | 说明 | 路径 |
|------|------|------|
| **06-cicd** | CI/CD 配置 | `modules/06-cicd/` |
| **07-profile** | GitHub Profile README | `modules/07-profile/` |
| **08-security** | 安全最佳实践 | `modules/08-security/` |
| **09-monorepo** | Monorepo 结构 | `modules/09-monorepo/` |
| **10-docs** | 文档网站集成 | `modules/10-docs/` |

### 高级模块

| 模块 | 说明 | 路径 |
|------|------|------|
| **11-versioning** | 版本管理策略 | `modules/11-versioning/` |
| **12-quality** | 代码质量工具 | `modules/12-quality/` |
| **13-community** | 社区建设 | `modules/13-community/` |
| **14-i18n** | 国际化支持 | `modules/14-i18n/` |
| **15-faq** | 常见问题 | `modules/15-faq/` |

---

## 快速参考

### 新仓库检查清单

- [ ] README.md 包含项目说明、安装、用法
- [ ] 选择了合适的 LICENSE
- [ ] 添加了 .gitignore
- [ ] 配置了 Topics 标签
- [ ] 设置了社交预览图
- [ ] 创建了 Issue/PR 模板
- [ ] 配置了分支保护规则
- [ ] 设置了 CI/CD 工作流
- [ ] 添加了 CONTRIBUTING.md（开源项目）
- [ ] 添加了 SECURITY.md（安全敏感项目）

### 推荐项目结构

```
project-name/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── workflows/
├── docs/
├── src/
├── tests/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
└── .gitignore
```

### 常用许可证

| 许可证 | 特点 | 适用场景 |
|--------|------|----------|
| **MIT** | 宽松，允许商用 | 大多数开源项目 |
| **Apache 2.0** | 专利保护 | 企业级项目 |
| **GPL-3.0** | 强制开源 | 保持开源的项目 |

---

## 使用方式

### 查看特定模块

```
请参考 modules/02-readme/ 了解 README 设计
```

### 按需组合

根据项目需求，选择相关模块：

- **小型工具库**: 01-structure + 02-readme + 03-config
- **开源项目**: 全部基础模块 + 06-cicd + 08-security
- **企业项目**: 基础模块 + 进阶模块 + 11-versioning + 12-quality
- **社区项目**: 全部模块

---

## 模块详情

### 02-readme 模块结构

```
modules/02-readme/
├── README.md      # README 设计指南
├── badges.md      # 徽章配置
└── tools.md       # 工具推荐
```

### 模块文件说明

每个模块包含：
- `README.md` - 模块主文档
- 可选的子文档 - 详细主题

---

## 版本信息

- **版本**: 2.0.0
- **架构**: 分包分级
- **模块数**: 15
- **更新日期**: 2024-01
