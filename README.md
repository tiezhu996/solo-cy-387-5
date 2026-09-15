# RentFind 租房与物业报修平台

```bash
cp .env.example .env
docker compose up -d --build
```

RentFind 面向房东、租客和物业人员，提供房源发布、搜索预约、合同管理和报修跟踪能力。

## 项目主要功能

- 房源发布：小区、户型、面积、租金、押金、付款方式、照片和设施。
- 搜索筛选：区域、价格、户型、面积、设施，并支持列表和地图视图切换。
- 预约看房：租客选择时间段，房东确认后生成通知。
- 合同管理：生成租赁合同模板并记录租期、租金、双方信息和状态。
- 物业报修：提交故障类型、描述和照片，物业接单并更新进度。
- 快递代收与取件：租客登记预计到达快递，物业按楼栋收件入库并生成取件凭证；随时查看待取件/已取件记录，取件时核对凭证推进状态，凭证不符、重复取件、单号查不到均返回明确错误。
- 角色区分：房东、租客、物业人员拥有不同工作台。

## 快速启动方式

首次启动前执行：

```bash
cp .env.example .env
docker compose up -d --build
```

访问地址：http://localhost:18407

## 本地开发方式

```bash
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py runserver 0.0.0.0:8000
cd frontend && npm install && npm run dev
```

## 运行测试

快递代收模块的测试基于 Django 测试框架，自动建库与清理数据，可重复运行：

```bash
cd backend
python manage.py test app.apps.packages     # 仅快递模块
python manage.py test                       # 全部测试
```

覆盖：登记（含重复单号、缺参）、入库生成 6 位凭证（含幂等、单号不存在）、正常取件、错误凭证、无效单号、取件后重复操作（取件时间不被改写）、待取件/待入库/已取件列表查询，以及并发取件竞态——同一待取件包裹被 8 个请求同时取走时仅一次成功，其余返回 `PACKAGE_ALREADY_PICKED`，最终状态与取件时间一致。

测试库按进程（PID + 随机后缀）隔离，因此可在不同终端同时运行多个 `manage.py test` 进程而互不干扰；每个进程结束时由 Django 自动删除自己的测试库（SQLite 删临时文件，PostgreSQL 删对应测试库）。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Element Plus、Vite、高德地图 JS API |
| 后端 | Python、Django、Django REST Framework |
| 数据库 | PostgreSQL |
| 认证 | JWT |
| 部署 | Docker Compose、Nginx |

## 项目目录结构

```text
.
├── backend
│   ├── app
│   │   └── apps
│   │       └── packages   # 快递代收与取件模块（models/services/views/serializers）
│   ├── database
│   └── manage.py
├── frontend
│   ├── src
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 环境变量说明

| 变量 | 说明 |
| --- | --- |
| COMPOSE_PROJECT_NAME | Compose 项目名，固定为 rentfind |
| DATABASE_URL | Django 连接 PostgreSQL 的地址 |
| DJANGO_SECRET_KEY | Django 密钥 |
| AMAP_KEY | 高德地图 JS API Key |

## Docker 部署说明

Compose 顶层声明 `name: rentfind`，容器名带 `rentfind-` 前缀，数据库和媒体文件分别使用命名卷持久化，前端 Nginx 将 `/api` 代理到后端 `backend:8000`。

## 快递代收与取件模块

状态流转：`待入库`（租客登记）→ `待取件`（物业按楼栋收件入库并生成 6 位取件凭证）→ `已取件`（核对单号+凭证后取件）。数据持久化在 PostgreSQL，刷新或重新进入页面后记录与状态仍在。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/packages/` | 租客登记预计到达的快递 |
| GET | `/api/packages/?state=pending` | 记录查询：`pending` 待取件 / `registered` 待入库 / `picked` 已取件，不带参数为全部 |
| POST | `/api/packages/store/` | 物业按楼栋收件入库并生成取件凭证 |
| POST | `/api/packages/pickup/` | 核对单号与凭证并完成取件 |

错误以统一格式 `{success:false, code, message}` 返回，前端直接展示 `message`：

| code | 触发场景 |
| --- | --- |
| `PACKAGE_DUPLICATE` | 快递单号已登记，禁止重复登记 |
| `PACKAGE_NOT_FOUND` | 入库或取件时单号查不到 |
| `INVALID_PICKUP_CODE` | 取件凭证与单号不匹配 |
| `PACKAGE_ALREADY_PICKED` | 对已取件包裹重复取件 |
| `PACKAGE_STATUS_INVALID` | 包裹尚未入库（无凭证）时尝试取件 |

## License

MIT
