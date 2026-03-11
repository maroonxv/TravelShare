# Issue 和 PR 模板

## Bug 报告模板

文件位置: `.github/ISSUE_TEMPLATE/bug_report.yml`

```yaml
name: Bug 报告
description: 报告一个 bug
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: 感谢你报告 bug！
  - type: textarea
    id: description
    attributes:
      label: Bug 描述
      description: 清晰描述这个 bug
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: 复现步骤
      description: 如何复现这个问题？
      placeholder: |
        1. 执行 '...'
        2. 点击 '...'
        3. 看到错误
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 期望行为
      description: 你期望发生什么？
  - type: input
    id: version
    attributes:
      label: 版本
      description: 使用的版本号
```

## 功能请求模板

文件位置: `.github/ISSUE_TEMPLATE/feature_request.yml`

```yaml
name: 功能请求
description: 提出新功能建议
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: 问题描述
      description: 描述你遇到的问题
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: 建议的解决方案
      description: 你希望如何解决这个问题？
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: 替代方案
      description: 你考虑过的其他方案
```

## Issue 模板配置

文件位置: `.github/ISSUE_TEMPLATE/config.yml`

```yaml
blank_issues_enabled: false
contact_links:
  - name: 讨论区
    url: https://github.com/USER/REPO/discussions
    about: 一般问题请在讨论区提问
  - name: 文档
    url: https://docs.example.com
    about: 查看文档获取帮助
```

## PR 模板

文件位置: `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## 描述

简要描述这个 PR 的更改内容。

## 更改类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构
- [ ] 其他

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 已添加/更新测试
- [ ] 已更新文档
- [ ] 所有测试通过

## 相关 Issue

Fixes #(issue number)
```

## 多 PR 模板

目录结构:
```
.github/
└── PULL_REQUEST_TEMPLATE/
    ├── bug_fix.md
    ├── feature.md
    └── docs.md
```

使用时在 URL 添加 `?template=bug_fix.md`
