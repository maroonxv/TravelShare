# 后端说明

TravelShare 后端采用 Flask + SQLAlchemy，负责认证、社交、行程、AI 助手和后台管理能力。

## 启动方式

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

服务默认运行在 `http://localhost:5001`。

## 关键配置

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy 数据库连接串 |
| `DEEPSEEK_API_KEY` | AI 对话能力所需的 DeepSeek Key |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址，默认官方地址 |

## 测试

```bash
cd backend
python -m pytest tests/integration/view/test_auth_view.py -q
```

说明：

- 上面的命令适合作为本地或 CI 的 smoke 测试。
- 完整 `python -m pytest` 会覆盖更多集成场景，但其中部分测试依赖 MySQL 与外部服务配置。

当前测试主要位于：

- `tests/unit/`
- `tests/integration/application_service/`
- `tests/integration/database/`
- `tests/integration/view/`
- `tests/integration/external_service/`

## 模块划分

- `src/app_auth/`
- `src/app_social/`
- `src/app_travel/`
- `src/app_ai/`
- `src/app_admin/`
- `src/shared/`

如果你是第一次看后端代码，建议先从 `src/app.py` 和 `src/shared/database/core.py` 开始。
