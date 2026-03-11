# 国际化支持

## 多语言 README

```
project/
├── README.md           # 默认（英文）
├── README.zh-CN.md     # 简体中文
├── README.ja.md        # 日文
└── README.ko.md        # 韩文
```

## 语言切换链接

```markdown
# Project Name

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)
```

## 语言代码规范

| 语言 | 代码 | 文件名 |
|------|------|--------|
| 英文 | en | README.md |
| 简体中文 | zh-CN | README.zh-CN.md |
| 繁体中文 | zh-TW | README.zh-TW.md |
| 日文 | ja | README.ja.md |
| 韩文 | ko | README.ko.md |
| 法文 | fr | README.fr.md |
| 德文 | de | README.de.md |
| 西班牙文 | es | README.es.md |

## 文档国际化

### VitePress

```
docs/
├── en/
│   └── index.md
├── zh/
│   └── index.md
└── .vitepress/
    └── config.ts
```

配置:
```ts
export default {
  locales: {
    root: {
      label: 'English',
      lang: 'en'
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN'
    }
  }
}
```

### Docusaurus

```
docs/
├── intro.md
└── i18n/
    └── zh-Hans/
        └── docusaurus-plugin-content-docs/
            └── current/
                └── intro.md
```

## 翻译工作流

### Crowdin 集成

```yaml
# crowdin.yml
project_id: "PROJECT_ID"
api_token_env: CROWDIN_TOKEN
base_path: "."
base_url: "https://api.crowdin.com"

files:
  - source: /docs/en/**/*.md
    translation: /docs/%two_letters_code%/**/%original_file_name%
```

### GitHub Action

```yaml
name: Crowdin Sync

on:
  push:
    branches: [main]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: crowdin/github-action@v1
        with:
          upload_sources: true
          download_translations: true
        env:
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_TOKEN }}
```
