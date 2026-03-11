<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-Skill-blue?style=for-the-badge" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/Modules-15-green?style=for-the-badge" alt="Modules">
  <img src="https://img.shields.io/badge/Templates-4-orange?style=for-the-badge" alt="Templates">
</p>

<h1 align="center">Repository Toolkit</h1>

<p align="center">
  <strong>Complete GitHub Repository Design Toolkit for Claude Code</strong>
  <br>
  <em>15 modules, 4 executable templates — covering repo setup, docs, collaboration, and quality</em>
</p>

<p align="center">
  <a href="#modules">Modules</a> •
  <a href="#templates">Templates</a> •
  <a href="#recipes">Recipes</a> •
  <a href="#quick-start">Quick Start</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-CLI-8A2BE2?logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white" alt="GitHub">
  <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

**English** | [中文](#中文)

---

## Overview

**Repository Toolkit** is a complete GitHub repository design toolkit organized by project phase. It evolved from a 15-module knowledge base into an actionable workflow system with routing, templates, and project-type recipes.

### What Changed (v2.0)

| Before (v1) | After (v2) |
|-------------|------------|
| 15 standalone modules | **5 phase-grouped workflows** |
| Knowledge-only guides | **Actionable templates included** |
| Linear difficulty levels | **Phase-based routing** |
| No quick actions | **Intent-based routing + recipes** |

---

## Modules

| # | Phase | Module | What It Covers |
|---|-------|--------|---------------|
| 01 | Setup | [structure](modules/01-structure/) | Project directory layout, essential files |
| 02 | Documentation | [readme](modules/02-readme/) | README design, badges, shields.io, tools |
| 03 | Setup | [config](modules/03-config/) | LICENSE, CONTRIBUTING, SECURITY, CODEOWNERS |
| 04 | Collaboration | [templates](modules/04-templates/) | Bug reports, feature requests, PR templates |
| 05 | Setup | [settings](modules/05-settings/) | Topics, social preview, branch protection |
| 06 | Quality | [cicd](modules/06-cicd/) | GitHub Actions workflows, CI/CD pipelines |
| 07 | Advanced | [profile](modules/07-profile/) | GitHub Profile README |
| 08 | Quality | [security](modules/08-security/) | Dependabot, CodeQL, secret scanning |
| 09 | Advanced | [monorepo](modules/09-monorepo/) | Monorepo structure and tooling |
| 10 | Documentation | [docs](modules/10-docs/) | Documentation site integration |
| 11 | Quality | [versioning](modules/11-versioning/) | SemVer, Conventional Commits, changelogs |
| 12 | Quality | [quality](modules/12-quality/) | Linting, pre-commit hooks, EditorConfig |
| 13 | Collaboration | [community](modules/13-community/) | Discussions, contributor recognition, sponsors |
| 14 | Documentation | [i18n](modules/14-i18n/) | Multi-language README, internationalization |
| 15 | Documentation | [faq](modules/15-faq/) | Frequently asked questions |

---

## Templates

Ready-to-use templates for common repository tasks:

| Template | Use Case |
|----------|----------|
| [new-repo-checklist](templates/new-repo-checklist.md) | Step-by-step checklist for setting up a new GitHub repo |
| [readme-template](templates/readme-template.md) | Universal README template for any project |
| [ci-workflow-template](templates/ci-workflow-template.yml) | GitHub Actions CI pipeline (lint, test, build, deploy) |
| [release-checklist](templates/release-checklist.md) | Release checklist (version bump, changelog, tag, publish) |

---

## Recipes

Module combinations by project type:

| Project Type | Modules | Templates |
|---|---|---|
| **Small utility / library** | 01 + 02 + 03 | new-repo-checklist, readme-template |
| **Open source project** | 01-06 + 08 + 11-13 | All templates |
| **Enterprise project** | 01-06 + 08 + 11 + 12 | ci-workflow-template, release-checklist |
| **Documentation-heavy** | 01-03 + 10 + 14 + 15 | readme-template |
| **Monorepo** | 01-03 + 06 + 09 + 11 + 12 | ci-workflow-template, release-checklist |

---

## Quick Start

### Installation

```bash
cd ~/.claude/skills
git clone https://github.com/LeoLin990405/github-repo-design-skill.git github-repo-design
```

### Usage

```bash
# The toolkit auto-routes based on your request:
"Set up a new repo"            → Setup modules + new-repo-checklist
"Create a README"              → readme module + readme-template
"Add CI/CD"                    → cicd module + ci-workflow-template
"Prepare a release"            → versioning module + release-checklist

# Or access modules directly:
"Use the security module"      → 08-security
"Show monorepo best practices" → 09-monorepo
```

---

## Structure

```
github-repo-design/
├── SKILL.md                        # Router (entry point)
├── README.md                       # This file
├── LICENSE
├── modules/                        # 15 knowledge modules
│   ├── 01-structure/
│   ├── 02-readme/
│   │   ├── README.md
│   │   ├── badges.md
│   │   └── tools.md
│   ├── 03-config/
│   ├── ...
│   └── 15-faq/
└── templates/                      # Executable templates
    ├── new-repo-checklist.md
    ├── readme-template.md
    ├── ci-workflow-template.yml
    └── release-checklist.md
```

---

## 中文

### 概述

**Repository Toolkit** 是一个完整的 GitHub 仓库设计工具集，按项目阶段组织。从 15 个知识模块进化为可执行的工作流系统，包含路由、模板和项目类型配方。

### 模块

| 阶段 | 模块 | 覆盖范围 |
|------|------|---------|
| 初始化 | 01-structure, 03-config, 05-settings | 目录结构、配置文件、仓库设置 |
| 文档 | 02-readme, 10-docs, 14-i18n, 15-faq | README、文档站点、国际化、FAQ |
| 协作 | 04-templates, 13-community | Issue/PR 模板、社区建设 |
| 质量 | 06-cicd, 08-security, 11-versioning, 12-quality | CI/CD、安全、版本管理、代码质量 |
| 高级 | 07-profile, 09-monorepo | Profile README、Monorepo |

### 模板

| 模板 | 用途 |
|------|------|
| new-repo-checklist | 新仓库搭建检查清单 |
| readme-template | 通用 README 模板 |
| ci-workflow-template | GitHub Actions CI 模板 |
| release-checklist | 发布检查清单 |

### 安装

```bash
cd ~/.claude/skills
git clone https://github.com/LeoLin990405/github-repo-design-skill.git github-repo-design
```

---

## Contributors

- **Leo** ([@LeoLin990405](https://github.com/LeoLin990405)) - Project Lead
- **Claude** (Anthropic Claude) - Content Generation

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with collaboration between human and AI</sub>
</p>
