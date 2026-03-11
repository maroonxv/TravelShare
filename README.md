# TravelShare

![Frontend](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Flask%203-000000?logo=flask&logoColor=white)
![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-4479A1?logo=mysql&logoColor=white)
![Project](https://img.shields.io/badge/Type-Course%20Project-1F6FEB)

TravelShare 是一个面向“行前规划、行中协作、行后分享”的旅行共享平台。项目采用前后端分离架构，前端基于 React + Vite，后端基于 Flask + SQLAlchemy，覆盖用户认证、社交广场、行程管理、即时聊天、AI 旅行助手和后台管理等能力。

## 项目亮点

- 旅行全周期闭环：从攻略准备、组队出行，到动态分享和互动社交。
- 领域拆分清晰：后端围绕 `auth`、`social`、`travel`、`ai`、`admin` 五个模块组织。
- 可演示可扩展：既适合课程答辩展示，也保留了后续拆分与持续演进空间。
- 仓库入口标准化：根目录新增统一文档入口、协作规范、Issue/PR 模板与 CI 工作流。

## 系统概览

```mermaid
flowchart LR
    UI["Frontend<br/>React + Vite"] --> API["Backend<br/>Flask + Socket.IO"]
    API --> AUTH["Auth"]
    API --> SOCIAL["Social"]
    API --> TRAVEL["Travel"]
    API --> ADMIN["Admin"]
    API --> AI["AI Assistant"]
    AUTH --> DB[("MySQL / SQLite")]
    SOCIAL --> DB
    TRAVEL --> DB
    ADMIN --> DB
    AI --> DEEPSEEK["DeepSeek API<br/>(optional)"]
```

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| `frontend/` | React + Vite 前端应用，负责页面、路由、组件和接口调用。 |
| `backend/` | Flask 后端服务，包含领域模块、数据库访问、接口视图和测试。 |
| `docs/` | 新增的仓库导航文档，面向开发者快速理解项目与协作流程。 |
| `doc/` | 原有课程文档与设计说明，保留现状，不打断正在进行的内容修订。 |
| `PlantUML/` | 架构图与建模素材。 |
| `.github/` | Issue/PR 模板与 CI 工作流。 |

更详细的目录说明见 [docs/repository-map.md](docs/repository-map.md)。

## 功能模块

- `Auth`：注册、登录、个人资料、密码修改与重置。
- `Travel`：行程创建、日程活动管理、成员协作、公共行程浏览。
- `Social`：动态发布、评论点赞、好友关系、聊天会话。
- `AI`：接入 DeepSeek 的旅行问答与辅助生成能力。
- `Admin`：后台数据查看与运营辅助能力。

## 技术栈

- 前端：React 19、Vite 7、React Router、Axios、Socket.IO Client
- 后端：Flask、Flask-Cors、SQLAlchemy、PyMySQL、Socket.IO
- AI：LangChain、langchain-openai、DeepSeek API
- 测试：Pytest
- 文档：Markdown、PlantUML、Mermaid

## 快速开始

### 环境要求

- Node.js 20+
- Python 3.10+
- MySQL 8+（可选；未配置时后端默认回退到 SQLite）

### 1. 启动后端

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
python src/app.py
```

后端默认运行在 `http://localhost:5001`。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，并通过 Vite 代理将 `/api` 和 `/static` 转发到后端服务。

### 3. 运行验证

```bash
# backend smoke test
cd backend
python -m pytest tests/integration/view/test_auth_view.py -q

# frontend
cd frontend
npm run lint
npm run build
```

如果你已经准备好了 MySQL、本地测试数据以及外部服务配置，也可以在 `backend/` 下执行完整的 `python -m pytest`。当前仓库中的部分集成测试依赖真实数据库或第三方接口，因此默认更推荐先跑上面的 smoke 流程。

## 配置说明

后端当前支持的关键环境变量：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DATABASE_URL` | 数据库连接串 | `sqlite:///./travel_sharing.db` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 无 |
| `DEEPSEEK_BASE_URL` | DeepSeek 服务地址 | `https://api.deepseek.com` |

示例配置见 [backend/.env.example](backend/.env.example)。

## 文档入口

- [docs/README.md](docs/README.md)：仓库文档导航
- [docs/getting-started.md](docs/getting-started.md)：本地开发与联调步骤
- [docs/repository-map.md](docs/repository-map.md)：仓库结构说明与维护约定
- [doc/requirements/](doc/requirements/)：课程需求文档
- [doc/design/](doc/design/)：架构设计与详细设计文档
- [TODO.md](TODO.md)：当前待办与后续计划

## 协作与规范

- 提交问题前，请先查看 [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)
- 提交代码前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)
- 协作行为约定见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 安全问题处理方式见 [SECURITY.md](SECURITY.md)
- 本次仓库规范化变更记录见 [CHANGELOG.md](CHANGELOG.md)

## 设计说明

这次仓库重构遵循以下原则：

- 不打断现有课程文档的编写节奏，因此保留 `doc/` 原目录不搬迁。
- 把“仓库入口层”统一到根目录和 `docs/`，让第一次进入项目的人更快找到启动方式。
- 用 GitHub 模板与 CI 兜住协作流程，减少后续维护成本。
