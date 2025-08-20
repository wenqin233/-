# AI个性化学习伴侣

## 项目概述

### 选择赛题
**知识奇点：教育的未来**

全球教育资源分配不均，多少天才因为没有得到充分的教育而无法发掘，我们需要一种新生的力量来打破教育壁垒。2018年，GPT3出现，大模型让我们看到了成本更低，更能惠及全球的，适合每一个人的"老师"，让所有人都享受到同等的教育资源似乎已经是一个可以望见的未来。

本项目借助大模型的力量，构建出一个为学习提升效率，或者为教育提升效率的工具。我们相信，这样的力量将会为学习带来革新，让每个人都能享受到个性化的教育，发掘自己的潜能。

### 项目创意
AI个性化学习伴侣是一个基于人工智能的个性化学习平台，旨在为用户提供定制化的学习体验。该平台通过分析用户的知识水平和学习行为，生成个性化的学习内容和路径，帮助用户高效地掌握新知识。

在传统的教育模式中，所有学生都接受相同的教学内容和进度，这忽略了每个学习者独特的知识背景和学习能力。我们的项目通过集成先进的大语言模型，为每个学习者创建专属的学习体验，真正实现因材施教。

### 核心理念
1. **个性化学习** - 根据用户的知识水平和学习目标定制内容
2. **智能评估** - 实时分析学习效果并调整学习路径
3. **交互式体验** - 提供与AI助手的实时对话功能
4. **进度可视化** - 清晰展示学习成果和进步轨迹

## 功能特点

### 1. 个性化学习内容生成
- 根据用户的学习目标和知识水平，自动生成个性化的学习材料
- 支持多种难度级别的内容（初级、中级、高级）
- 内容涵盖编程、机器学习等多个领域

### 2. 智能知识评估
- 通过练习题分析用户的知识掌握情况
- 构建用户知识图谱，可视化知识掌握程度
- 持续更新用户知识状态

### 3. 个性化学习路径规划
- 根据用户当前知识水平，推荐最适合的学习路径
- 动态调整学习计划，确保学习效率最大化

### 4. 交互式学习体验
- 提供交互式对话功能，用户可以与AI进行学习相关的对话
- 实时反馈和解释，帮助用户理解复杂概念



## 技术架构

### 后端技术栈
- **框架**: Python Flask
- **数据库**: MongoDB
- **认证**: 基于JWT的会话管理
- **异步任务**: Celery + Redis
- **AI服务**: 阿里云百炼API

### 前端技术栈
- **模板引擎**: Jinja2 (Flask内置)
- **样式**: 原生CSS
- **交互**: 原生JavaScript

### 项目结构
```
project/
├── app.py                 # 主应用文件
├── auth.py                # 用户认证模块
├── config.py              # 配置文件
├── database.py            # 数据库操作模块
├── progress_tracker.py    # 学习进度跟踪模块
├── tasks.py               # 异步任务定义
├── requirements.txt       # 项目依赖
├── .env.example          # 环境变量示例
├── models/               # 数据模型
│   ├── user.py           # 用户模型
│   └── lesson.py         # 课程模型
├── utils/                # 工具模块
│   ├── content_generator.py      # 内容生成器
│   ├── knowledge_analyzer.py     # 知识分析器
│   ├── learning_path_planner.py  # 学习路径规划器
│   ├── feedback_processor.py     # 反馈处理器
│   ├── progress_visualizer.py    # 进度可视化工具
│   ├── security.py               # 安全工具
│   ├── validators.py             # 数据验证器
│   └── response.py               # 响应工具
├── templates/            # 前端模板
│   ├── dashboard.html    # 仪表板页面
│   ├── lesson.html       # 课程页面
│   ├── exercise.html     # 练习页面
│   ├── login.html        # 登录页面
│   ├── register.html     # 注册页面
│   └── index.html        # 首页
├── static/               # 静态资源
│   └── style.css         # 样式文件
└── docs/                 # 文档
    └── api.md            # API文档
```

## 环境配置

1. 在`.env`文件中根据您的实际配置替换占位符值：
* your-secret-key-here → 替换为实际的 Flask 密钥
* your-dashscope-api-key-here → 替换为实际的阿里云百炼 API 密钥
* mongodb://localhost:27017/ai_learning_companion → 根据实际 MongoDB 配置修改
* your-jwt-secret-key-here → 替换为实际的 JWT 密钥
* Redis 相关配置根据实际 Redis 服务器信息修改
  
1. 配置必要的环境变量：
   - `DASHSCOPE_API_KEY`: 阿里云百炼API密钥
   - `MONGO_URI`: MongoDB连接字符串
   - `JWT_SECRET_KEY`: JWT密钥
   - `REDIS_URL`: Redis连接字符串
### 以下为实例
```
 # Flask配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# LLM API配置（如OpenAI或阿里云百炼）
DASHSCOPE_API_KEY=你的APIkey
# OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# 数据库配置
MONGO_URI=mongodb://localhost:27017/ai_learning_companion

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis配置（用于Celery）
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```
## 安装与运行

### 本地开发环境

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
* PS:若安装依赖报错请尝试以下方法
* 1.安装pip
* 2.安装Microsoft C++ 生成工具 https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/

2. 安装MongoDB数据库：https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.12-signed.msi


3. 启动应用：
   ```bash
   python app.py
   ```

4. 访问应用：
   打开浏览器访问 `http://localhost:5000`

## API接口

### 认证相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

### 学习相关
- `POST /api/analyze-knowledge` - 分析用户知识水平
- `POST /api/generate-lesson` - 生成个性化课程内容
- `POST /api/complete-lesson` - 完成课程记录
- `POST /api/exercise-feedback` - 处理练习反馈
- `POST /api/personalized-path` - 生成个性化学习路径
- `POST /api/interactive-chat` - 交互式对话学习

### 进度跟踪相关
- `GET /api/progress` - 获取学习进度
- `GET /api/learning-history` - 获取学习历史
- `GET /api/knowledge-graph` - 获取用户知识图谱
- `POST /api/knowledge-graph` - 更新用户知识图谱
- `GET /api/progress-summary` - 获取学习进度摘要
- `GET /api/learning-report` - 获取学习报告

### 内容相关
- `GET /api/topics` - 获取所有可用学习主题
- `GET /api/recommendations` - 获取学习主题推荐



## 可执行成果

目前项目为Web应用，可通过本地运行或部署到服务器访问。

 **Web应用** - 可通过浏览器访问的学习平台`http://103.40.14.38:40000`


访问方式：
- 本地运行：启动应用后访问 `http://localhost:5000`
- 在线部署：部署到服务器后通过域名访问 `http://103.40.14.38:40000`

## 开发路线图

### 已完成功能
- ~~基础问答接口和知识评估模块~~
- ~~用户认证和会话管理~~
- ~~个性化课程内容生成~~
- ~~学习进度跟踪和可视化~~
- ~~交互式对话学习功能~~

### 后续优化方向
- 增加更多学习主题和内容
- 优化AI模型响应质量和准确性
- 增强移动端适配和用户体验
- 添加社交学习功能
- 实现更精细的学习分析和推荐算法

