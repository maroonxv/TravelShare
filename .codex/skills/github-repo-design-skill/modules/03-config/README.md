# 核心配置文件

## 1. LICENSE - 开源许可证

### 常用许可证选择

| 许可证 | 特点 | 适用场景 |
|--------|------|----------|
| **MIT** | 宽松，允许商用 | 大多数开源项目 |
| **Apache 2.0** | 专利保护，商用友好 | 企业级项目 |
| **GPL-3.0** | 强制开源衍生作品 | 希望保持开源的项目 |
| **BSD-3-Clause** | 宽松，需保留版权声明 | 学术项目 |
| **CC0** | 公共领域 | 数据集、文档 |

## 2. CONTRIBUTING.md - 贡献指南

```markdown
# 贡献指南

感谢你考虑为本项目做出贡献！

## 如何贡献

### 报告 Bug

1. 确认 bug 尚未被报告
2. 使用 Bug 报告模板创建 Issue
3. 提供详细的复现步骤

### 提交功能请求

1. 先搜索是否已有类似请求
2. 使用功能请求模板创建 Issue
3. 清晰描述需求和用例

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

## 代码规范

- 遵循项目现有的代码风格
- 添加必要的测试
- 更新相关文档

## 行为准则

请阅读我们的 [行为准则](CODE_OF_CONDUCT.md)
```

## 3. CODE_OF_CONDUCT.md - 行为准则

推荐使用 [Contributor Covenant](https://www.contributor-covenant.org/) 模板。

## 4. SECURITY.md - 安全策略

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

## 5. CODEOWNERS - 代码所有者

```
# 默认所有者
* @username

# 特定目录所有者
/docs/ @docs-team
/src/api/ @api-team
*.js @frontend-team

# 特定文件
package.json @maintainer
```

## 6. .gitignore - 忽略规则

```gitignore
# 依赖
node_modules/
vendor/
__pycache__/

# 构建产物
dist/
build/
*.egg-info/

# 环境配置
.env
.env.local
*.local

# IDE
.idea/
.vscode/
*.swp

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/

# 测试覆盖率
coverage/
.nyc_output/
```
