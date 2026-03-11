# 贡献指南

感谢你愿意为 TravelShare 做出改进。这个仓库目前既服务于课程项目交付，也希望保持可读、可维护、可继续演进的结构。

## 开始之前

提交改动前，建议先完成下面几件事：

1. 阅读根目录的 [README.md](README.md) 和 [docs/README.md](docs/README.md)。
2. 确认你的改动属于哪一层：
   - 业务代码：`frontend/` 或 `backend/`
   - 仓库说明：`docs/`
   - 课程交付文档：`doc/`
3. 尽量避免把生成产物、依赖目录和私有配置提交到仓库。

## 分支建议

推荐使用清晰的分支命名：

- `feature/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`
- `refactor/<short-name>`

## 提交建议

提交信息尽量简洁明确，建议体现“改了什么”和“为什么改”：

```text
feat: add trip member invitation flow
fix: handle empty avatar url on profile page
docs: reorganize repository entry docs
```

## 提交前检查

### 前端改动

```bash
cd frontend
npm run lint
npm run build
```

### 后端改动

```bash
cd backend
python -m pytest
```

## 文档维护约定

- 新的仓库说明、开发文档、协作文档放到 `docs/`。
- 需求、设计、项目计划等课程交付物继续维护在 `doc/`。
- 如需更新架构图，优先同步 `PlantUML/` 中的源文件。

## Issue 与 Pull Request

- Bug 反馈请优先使用 Bug 模板。
- 新功能建议请说明使用场景、收益和影响范围。
- PR 请尽量保持单一主题，方便审阅和回归验证。

## 安全相关

如果发现安全问题，请不要公开提交漏洞细节。处理方式见 [SECURITY.md](SECURITY.md)。
