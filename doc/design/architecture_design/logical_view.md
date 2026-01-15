# 逻辑视图 (Logical View)

## 1. 简介

逻辑视图 (Logical View) 关注系统如何满足功能需求。它通过抽象和分解，将复杂的系统划分为一系列相互协作的逻辑单元（包、子系统、类），并描述它们之间的静态结构和动态行为。

本项目采用**领域驱动设计 (DDD)** 方法论，逻辑架构主要由**限界上下文 (Bounded Contexts)** 和**分层架构 (Layered Architecture)** 共同定义。本视图将详细展示系统的逻辑组件、职责分配以及它们如何协作完成核心业务流程。

---

## 2. 顶层包结构与逻辑分区

系统在逻辑上被划分为五个高内聚、低耦合的子系统（即限界上下文），每个子系统对应代码库中的一个独立 Python 包。

### 2.1 模块划分

| 逻辑子系统 | 包名 (`backend/src/`) | 核心职责 |
| :--- | :--- | :--- |
| **认证与授权子系统** | `app_auth` | 管理用户身份 (Identity)、鉴权 (Authorization) 和会话安全。 |
| **旅行核心子系统** | `app_travel` | 处理行程规划、路线计算、预算管理及多人协作。 |
| **社交互动子系统** | `app_social` | 管理社区动态 (Posts)、评论互动及实时聊天 (Chat)。 |
| **AI 助手子系统** | `app_ai` | 提供基于 RAG 的智能问答、行程建议生成。 |
| **后台管理子系统** | `app_admin` | 提供系统级的数据监控与资源管理界面。 |

### 2.2 共享内核 (Shared Kernel)

除了上述业务子系统外，存在一个 `shared` 包，作为共享内核。
*   **职责**：存放通用的基础设施代码、工具类和跨上下文的协议定义。
*   **包含组件**：
    *   `EventBus`: 简单的进程内事件总线，用于解耦业务逻辑。
    *   `DomainEvent`: 所有领域事件的基类。
    *   `AppException`: 统一异常处理基类。
    *   `JsonEncoder`: 定制的 JSON 序列化工具。

---

## 3. 详细子系统设计

### 3.1 旅行核心子系统 (Travel Context)

这是整个应用最复杂的业务核心，采用了严格的充血模型。

#### 3.1.1 类与对象模型
*   **聚合根 (Aggregate Root) - `Trip`**:
    *   它是行程数据一致性的守护者。
    *   **属性**: `id`, `creator_id`, `status` (Planning/Ongoing/Completed), `budget`, `visibility`.
    *   **核心逻辑**:
        *   `start_trip()`: 校验当前状态，更新状态为 Ongoing，记录开始时间，触发 `TripStartedEvent`。
        *   `add_member(user_id, role)`: 校验操作权限及用户是否已存在。
        *   `update_budget(amount)`: 变更预算。
*   **实体 (Entities)**:
    *   **`TripDay`**: 代表行程中的某一天。负责管理当天的活动序列 (`activities` list)。
        *   逻辑: `reorder_activities()` 保证活动按时间或顺序排列。
    *   **`Activity`**: 具体的游玩项目。包含 `location` (经纬度), `start_time`, `end_time`。
    *   **`Transit`**: 活动之间的交通方式。连接两个 Activity。
*   **领域服务 (Domain Service) - `ItineraryService`**:
    *   处理跨实体的复杂计算。例如，当用户在某一天添加了 5 个活动，该服务负责调用地图 API 计算最佳路径，或者重新计算所有活动的总时长和预估交通费用。

#### 3.1.2 逻辑分层实现
*   **Interface (View)**: `travel_view.py` 接收 `POST /trips` 请求，解析 JSON。
*   **Application (Service)**: `TravelService` 开启事务，调用 `Trip` 构造函数创建对象，调用 `ITripRepository.save()`，最后提交事务。
*   **Infrastructure**: `TripRepositoryImpl` 将 `Trip` 对象拆解为 `TripPO`, `TripDayPO`, `ActivityPO` 等多张表的记录存入 MySQL。

---

### 3.2 社交互动子系统 (Social Context)

社交子系统包含“社区广场”和“即时通讯”两个主要逻辑分支。

#### 3.2.1 社区动态 (Feed)
*   **聚合根 - `Post`**:
    *   代表一篇游记或动态。
    *   **关系**: 包含多个 `PostImage`，拥有多个 `Comment` 和 `Like`。
    *   **逻辑**: 发布时需关联具体的 `Trip` (可选)。删除时需逻辑删除 (Soft Delete)。
*   **应用逻辑**:
    *   `SocialService.get_feed(tags)`: 复杂的查询逻辑。根据标签筛选，按时间倒序，并可能涉及“好友可见”等权限过滤。

#### 3.2.2 即时通讯 (Chat)
*   **聚合根 - `Conversation`**:
    *   代表一个聊天会话（私聊或群聊）。
    *   管理 `participants` (参与者列表)。
*   **实体 - `Message`**:
    *   消息内容，包含文本或图片 URL。
    *   逻辑: 消息一旦发送 (Sent)，状态流转为 Delivered -> Read。
*   **实时交互逻辑**:
    *   前端通过 Socket.IO 连接。
    *   后端 `socket_handlers.py` 监听 `join` 事件，将用户 socket 加入 `room_<conversation_id>`。
    *   当 `SocialService.send_message()` 成功保存消息后，触发 `MessageSentEvent`。
    *   事件监听器捕获事件，通过 `socketio.emit` 向特定房间广播消息。

---

### 3.3 AI 助手子系统 (AI Context)

该子系统逻辑上是一个管道 (Pipeline) 结构，处理数据流。

#### 3.3.1 RAG (检索增强生成) 逻辑流
1.  **Query Pre-processing**: `AiService` 接收用户提问，提取关键词。
2.  **Retrieval (检索器)**: `Retriever` 组件查询 `Travel` 和 `Social` 数据库。
    *   *逻辑*: 搜索用户的历史行程、公开的高赞游记、相关的地点信息。
3.  **Context Construction**: 将检索到的文本片段组装成 Prompt Context。
4.  **Generation**: 调用 LLM (DeepSeek) 生成回复。
5.  **Post-processing**: 格式化输出，提取回复中提到的地点生成“推荐卡片” (JSON 数据)。

---

### 3.4 认证子系统 (Auth Context)

*   **核心类 - `User`**:
    *   虽然在数据库中是核心表，但在 DDD 逻辑视图中，其他子系统通常只引用 `user_id`，而不直接持有 `User` 对象，以降低耦合。
*   **安全逻辑**:
    *   `PasswordService`: 负责 Hash 加盐存储和校验。
    *   `TokenService`: 生成和验证 JWT。拦截所有请求解析 Header 中的 Token，构建 `CurrentUser` 上下文对象。

---

## 4. 关键设计模式应用

为了解决特定的逻辑问题，系统中广泛应用了标准设计模式。

### 4.1 领域驱动设计 (DDD) 模式
*   **充血模型 (Rich Domain Model)**: 业务逻辑（如校验、状态流转、计算）封装在实体类中，而非 Service 类中。Service 类主要负责协调。
*   **仓储模式 (Repository)**: 屏蔽底层数据访问细节。逻辑层只依赖 `ITripRepository` 接口，不知道底层是 MySQL 还是 MongoDB。
*   **值对象 (Value Object)**: 如 `Money` (金额+币种), `GeoLocation` (经度+纬度)。它们是不可变的，逻辑上通过替换整个对象来修改值。

### 4.2 GoF 设计模式
*   **工厂模式 (Factory)**: 用于创建复杂的聚合根。例如，创建 `Trip` 时需要同时初始化默认的 `TripDay` 和创建者 Member 记录，这些逻辑封装在 `TripFactory` 或构造函数中。
*   **观察者模式 (Observer/Pub-Sub)**: 实现领域事件机制。`EventBus` 是 Subject，各 `Handler` 是 Observer。例如，`TripNotificationHandler` 观察 `TripInviteEvent`。
*   **策略模式 (Strategy)**: 在 RAG 模块中，检索策略可以是 `KeywordSearchStrategy` 或 `VectorSearchStrategy` (预留扩展)，根据配置动态切换。
*   **适配器模式 (Adapter)**: `Infrastructure` 层中的 `DeepSeekAdapter` 封装了具体的 HTTP API 调用，向领域层暴露统一的 `ILlmClient` 接口。

---

## 5. 组件交互逻辑 (Component Interaction)

### 5.1 场景一：创建行程并邀请好友
1.  **用户请求**: 前端发送 POST 请求到 `travel_view`。
2.  **服务编排**: `TravelService` 接收 DTO。
3.  **领域行为**: 创建 `Trip` 聚合根。调用 `trip.add_member(creator)`.
4.  **持久化**: `Repository` 保存 `Trip` 及其关联数据。
5.  **事件触发**: `TravelService` 收集 `TripCreatedEvent` 并发布。
6.  **跨子系统交互**:
    *   (异步) `app_social` 中的监听器收到事件，在用户的 Timeline 中生成一条“开始了一段新旅程”的动态（如果行程公开）。
    *   (异步) `app_ai` 可能在后台预加载该目的地的攻略数据进入缓存。

### 5.2 场景二：AI 问答
1.  **请求**: 用户在聊天框发送 "帮我规划去大理的行程"。
2.  **处理**: `app_ai.AiService` 接收请求。
3.  **跨模块读取**: `AiService` 通过 `Retriever` (基础设施层) 直接读取 `Travel` 表中的公共行程数据作为参考（这是读操作的适度耦合，为了性能通常允许）。
4.  **生成**: LLM 返回建议。
5.  **响应**: 结果通过 SSE (Server-Sent Events) 流式返回给前端。

---

## 6. 数据流与控制流 (Data & Control Flow)

### 6.1 标准 HTTP 请求处理流
系统遵循严格的单向依赖流：

`Client (Browser)` -> `View (Controller)` -> `Application Service` -> `Domain Model` -> `Infrastructure (Repository)` -> `Database`

*   **入站 (Inbound)**: JSON 数据在 View 层被校验，转化为 DTO 或直接参数传给 Service。Service 可能会从 Repository 加载 Domain Object。
*   **处理 (Processing)**: 业务逻辑在 Domain Object 内部执行，修改对象状态。
*   **出站 (Outbound)**: 只有 Domain Object 的“快照”或 DTO 会被返回给 View 层序列化为 JSON。Repository 负责将变更写回数据库。

### 6.2 实时消息流 (WebSocket)
`Client A` -> `Socket Event Handler` -> `SocialService` -> `Database`
                                             |
                                             v
                                        `EventBus` -> `Socket Emitter` -> `Client B`

---

## 7. 异常处理与事务逻辑

*   **事务边界**: 默认情况下，每个 HTTP 请求对应一个数据库 Session。Application Service 的方法被视为一个原子工作单元。如果 Service 执行过程中抛出异常，整个 Session 回滚。
*   **逻辑异常**: 使用自定义异常（如 `TripNotFoundError`, `OverBudgetException`）。View 层捕获这些异常，映射为 404 Not Found 或 400 Bad Request，而不是 500 Internal Server Error。

## 8. 总结

本逻辑视图展示了一个结构清晰、职责分明的系统架构。通过 DDD 的应用，业务逻辑被妥善地保护在领域层核心，而社交、AI 等辅助功能作为独立的上下文与其松耦合协作。这种设计不仅清晰地表达了当前的业务需求，也为未来功能的扩展（如增加新的 AI 能力或社交玩法）提供了灵活的逻辑基础。
