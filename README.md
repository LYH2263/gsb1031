# 📚 图书管理系统 (Library Management System)

一个基于现代 Web 技术栈构建的图书管理平台，提供优雅的用户界面和流畅的交互体验。支持用户借阅、归还图书，以及管理员对图书资源的增删改查管理。

## ✨ 功能特性

### � 用户端
- **账户系统**：手机号注册/登录，支持短信验证码流程（模拟）。
- **图书浏览**：
  - 瀑布流/网格布局展示图书。
  - 实时搜索（支持书名、作者、ISBN）。
  - 分页浏览。
- **借阅管理**：
  - 实时查看图书库存状态。
  - 一键借阅/归还。
  - 借阅状态可视化：
    - 🔵 **正在借阅中**：清晰的蓝色状态徽章。
    - 🟢 **读过**：历史借阅记录标记。
- **响应式设计**：
  - 完美适配桌面端大屏与移动端小屏。
  - 移动端优化的操作按钮与布局。

### 🛡️ 管理员端
- **图书管理**：
  - 添加新书（自动填充默认封面）。
  - 编辑图书信息（含库存管理）。
  - 删除图书（带安全确认模态框）。
- **权限控制**：基于角色的访问控制 (RBAC)。

## �🛠 技术栈

### Frontend (前端)
- **核心框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 组件库**: Ant Design (AntD)
- **样式方案**: Tailwind CSS (支持 Glassmorphism 玻璃拟态风格)
- **路由管理**: React Router v6
- **状态管理**: Context API

### Backend (后端)
- **Web 框架**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **数据库**: SQLite (轻量级，易于部署)
- **认证**: JWT (JSON Web Tokens)
- **验证**: Pydantic

### DevOps
- **容器化**: Docker & Docker Compose
- **服务编排**: Nginx (前端静态资源服务)

## 🚀 快速启动 (Docker 推荐)

最简单的运行方式是使用 Docker Compose，一键启动所有服务。

1. **前置要求**：确保已安装并启动 Docker Desktop。
2. **启动服务**：
   在项目根目录下执行：
   ```bash
   docker compose up
   ```
3. **访问应用**：
   - **前端页面**: [http://localhost:3000](http://localhost:3000)
   - **后端 API 文档**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 💻 本地开发指南

如果您想在本地进行开发或调试，请按照以下步骤操作。

### 后端 (Backend)
```bash
cd library-management/backend

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端 (Frontend)
```bash
cd library-management/frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```
前端默认运行在 [http://localhost:5173](http://localhost:5173)，API 请求会代理到本地 8000 端口。

## 🧪 测试账号

系统初始化时会自动创建以下测试账号，登录页面也提供了一键填充功能：

| 角色 | 手机号 | 密码 | 权限 |
|------|--------|------|------|
| **管理员** | `13900000000` | `password` | 拥有所有图书管理权限 |
| **普通用户** | `13800000000` | `password` | 仅限借阅与查看 |

## 📂 项目结构

```
library-management/
├── backend/                 # FastAPI 后端
│   ├── main.py             # 入口文件
│   ├── models.py           # 数据库模型
│   ├── schemas.py          # Pydantic 模式
│   ├── crud.py             # 数据库操作
│   ├── database.py         # 数据库连接配置
│   ├── seed.sql            # 初始化数据
│   └── requirements.txt    # Python 依赖
├── frontend/                # React 前端
│   ├── src/
│   │   ├── components/     # 公共组件
│   │   ├── pages/          # 页面组件 (BookList, Login, etc.)
│   │   ├── context/        # 全局状态 (Auth)
│   │   └── services/       # API 请求封装
│   ├── index.html
│   ├── tailwind.config.js  # Tailwind 配置
│   └── vite.config.ts      # Vite 配置
├── docker-compose.yml       # Docker 编排文件
└── README.md                # 项目说明
```

## 📝 注意事项

- **数据持久化**: 在 Docker 模式下，SQLite 数据库文件存储在 Docker Volume `sqlite-data` 中，重启容器数据不会丢失。
- **端口占用**: 请确保本地 3000 和 8000 端口未被占用。
