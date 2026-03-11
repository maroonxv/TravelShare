# 代码质量工具

## Linting 配置

### JavaScript/TypeScript

文件位置: `.eslintrc.json`

```json
{
  "extends": ["eslint:recommended", "prettier"],
  "env": { "node": true, "es2022": true }
}
```

### Python

文件位置: `pyproject.toml`

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.black]
line-length = 88
```

## Pre-commit Hooks

文件位置: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### 安装和使用

```bash
# 安装
pip install pre-commit

# 安装 hooks
pre-commit install

# 手动运行
pre-commit run --all-files
```

## EditorConfig

文件位置: `.editorconfig`

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false

[*.py]
indent_size = 4
```

## Prettier 配置

文件位置: `.prettierrc`

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

## 代码质量 CI

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check
```

## 工具推荐

| 语言 | Linter | Formatter |
|------|--------|-----------|
| JavaScript | ESLint | Prettier |
| TypeScript | ESLint | Prettier |
| Python | Ruff | Black/Ruff |
| Go | golangci-lint | gofmt |
| Rust | clippy | rustfmt |
