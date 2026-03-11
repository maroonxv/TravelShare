# 仓库结构说明

TravelShare 当前采用“根目录统一入口 + 前后端独立开发 + 原有课程文档保留”的仓库组织方式。

## 顶层目录

```text
.
|-- .github/        # GitHub 模板与 CI
|-- backend/        # Flask 后端、测试、脚本与环境示例
|-- docs/           # 新增的仓库导航与开发者文档
|-- doc/            # 原有课程需求、设计、项目管理文档
|-- frontend/       # React 前端应用
|-- PlantUML/       # UML/架构图源文件
|-- README.md       # 根入口
`-- TODO.md         # 待办事项
```

## 后端结构

```text
backend/
|-- src/
|   |-- app.py
|   |-- app_auth/
|   |-- app_social/
|   |-- app_travel/
|   |-- app_ai/
|   |-- app_admin/
|   `-- shared/
|-- tests/
|-- scripts/
|-- requirements.txt
`-- .env.example
```

说明：

- `app_auth/`：认证与用户资料相关能力。
- `app_social/`：动态、评论、好友、聊天相关能力。
- `app_travel/`：行程、活动、成员协同与路线相关能力。
- `app_ai/`：AI 旅行助手与检索增强相关能力。
- `app_admin/`：后台管理能力。
- `shared/`：数据库连接、Socket.IO 等跨模块共享基础设施。

## 前端结构

```text
frontend/
|-- src/
|   |-- api/
|   |-- components/
|   |-- context/
|   |-- hooks/
|   |-- pages/
|   |-- styles/
|   `-- admin/
|-- public/
|-- package.json
`-- vite.config.js
```

说明：

- `api/`：按业务领域封装接口请求。
- `pages/`：页面级组件，按 `auth`、`social`、`travel`、`ai` 等业务拆分。
- `components/`：跨页面复用组件。
- `context/` 与 `hooks/`：全局状态与复用逻辑。

## 文档结构

- `docs/`：新的仓库入口文档。
- `doc/requirements/`：需求规格说明。
- `doc/design/architecture_design/`：架构视图。
- `doc/design/detailed_design/`：接口与详细设计。
- `doc/project_management/`：计划与过程材料。
- `PlantUML/plantuml_code/`：图表源文件。

## 维护约定

- 仓库级文档优先新增到 `docs/`。
- 课程交付文档继续维护在 `doc/`，避免和仓库说明混用。
- 不提交本地构建产物、依赖目录、虚拟环境和私有环境变量。
- 根目录只保留高层入口文件，不堆叠零散说明文档。
