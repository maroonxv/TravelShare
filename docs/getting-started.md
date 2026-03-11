# 快速开始

本文档面向首次运行 TravelShare 的开发者，覆盖最短启动链路与常用联调命令。

## 环境准备

- Node.js 20+
- Python 3.10+
- 可选：MySQL 8+

后端未配置 `DATABASE_URL` 时会自动回退到本地 SQLite，因此本地演示不一定强依赖 MySQL。

## 启动后端

```bash
cd backend
python -m venv .venv
```

激活虚拟环境：

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

安装依赖并准备配置：

```bash
pip install -r requirements.txt
copy .env.example .env
```

启动服务：

```bash
python src/app.py
```

默认地址：

- API 服务：`http://localhost:5001`
- 健康检查：`http://localhost:5001/health`

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：

- Web 应用：`http://localhost:5173`

## 前后端联调说明

- 前端通过 `frontend/vite.config.js` 将 `/api` 与 `/static` 代理到 `http://localhost:5001`。
- 默认开发模式下不需要额外配置前端环境变量。
- 如果需要启用 AI 对话，请在后端 `.env` 中补充 `DEEPSEEK_API_KEY`。

## 常用命令

### 后端

```bash
cd backend
python -m pytest tests/integration/view/test_auth_view.py -q
```

### 前端

```bash
cd frontend
npm run lint
npm run build
```

## 常见问题

### 后端无法连接数据库

- 先检查 `backend/.env` 中的 `DATABASE_URL`。
- 如果只是本地体验，可先删除该变量，使用默认 SQLite 启动。

### AI 接口不可用

- 确认已配置 `DEEPSEEK_API_KEY`。
- 如使用代理服务，检查 `DEEPSEEK_BASE_URL` 是否正确。

### 全量后端测试失败

- 当前部分集成测试依赖 MySQL 与真实第三方服务。
- 如果只是验证本地开发链路，优先运行 `tests/integration/view/test_auth_view.py` 这类 smoke 测试。

### 聊天或上传静态资源失败

- 确认后端已正常启动。
- 确认浏览器请求是否被代理到 `5001` 端口。
