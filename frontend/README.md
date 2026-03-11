# 前端说明

TravelShare 前端基于 React + Vite，负责认证、社交、行程与 AI 页面交互，并通过 Vite 代理与本地 Flask 服务联调。

## 启动方式

```bash
cd frontend
npm install
npm run dev
```

默认访问地址：`http://localhost:5173`

## 可用命令

```bash
npm run dev
npm run lint
npm run build
npm run preview
```

## 目录说明

- `src/api/`：接口封装
- `src/components/`：复用组件
- `src/context/`：全局状态
- `src/hooks/`：复用 hooks
- `src/pages/`：业务页面
- `src/admin/`：后台相关页面或模块
- `src/styles/`：主题和全局样式

## 开发说明

- `/api` 和 `/static` 请求会被代理到 `http://localhost:5001`。
- 当前前端没有强制要求的 `VITE_*` 环境变量。
- 若接口访问异常，优先确认后端是否已启动。
