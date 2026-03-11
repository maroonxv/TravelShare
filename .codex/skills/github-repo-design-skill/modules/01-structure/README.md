# 仓库核心文件结构

## 推荐的项目结构

```
project-name/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── (详细文档)
├── src/
│   └── (源代码)
├── tests/
│   └── (测试文件)
├── README.md              # 必需 - 项目说明
├── LICENSE                # 必需 - 开源许可证
├── CONTRIBUTING.md        # 推荐 - 贡献指南
├── CODE_OF_CONDUCT.md     # 推荐 - 行为准则
├── SECURITY.md            # 推荐 - 安全策略
├── CHANGELOG.md           # 推荐 - 变更日志
├── CITATION.cff           # 可选 - 引用信息
└── .gitignore             # 必需 - 忽略规则
```

## 文件优先级

| 优先级 | 文件 | 说明 |
|--------|------|------|
| 必需 | README.md | 项目说明 |
| 必需 | LICENSE | 开源许可证 |
| 必需 | .gitignore | 忽略规则 |
| 推荐 | CONTRIBUTING.md | 贡献指南 |
| 推荐 | CODE_OF_CONDUCT.md | 行为准则 |
| 推荐 | SECURITY.md | 安全策略 |
| 推荐 | CHANGELOG.md | 变更日志 |
| 可选 | CITATION.cff | 引用信息 |

## 目录说明

| 目录 | 用途 |
|------|------|
| `.github/` | GitHub 特定配置 |
| `docs/` | 详细文档 |
| `src/` | 源代码 |
| `tests/` | 测试文件 |
| `examples/` | 示例代码 |
| `scripts/` | 构建/部署脚本 |
