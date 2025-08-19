# AI个性化学习伴侣 API 文档

## 认证

大部分API端点需要认证。认证通过在请求头中添加`Authorization`字段实现：

```
Authorization: Bearer <token>
```

用户首先需要通过`POST /api/register`注册账户，然后通过`POST /api/login`获取访问令牌。

## 响应格式

所有API响应都遵循统一的格式：

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

### 分页响应
```json
{
  "success": true,
  "message": "获取成功",
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误信息"
}
```

## API端点

### 公共端点

#### 获取系统信息
```
GET /
```

响应:
```json
{
  "success": true,
  "data": {
    "message": "AI个性化学习伴侣 API",
    "version": "1.0.0"
  }
}
```

#### 健康检查
```
GET /health
```

响应:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "AI个性化学习伴侣"
  }
}
```

#### 获取可用学习主题
```
GET /api/topics
```

响应:
```json
{
  "success": true,
  "data": [
    {
      "id": "python_basics",
      "name": "Python基础",
      "key_points": ["变量", "数据类型", "控制结构"]
    }
  ]
}
```

#### 用户注册
```
POST /api/register
```

请求体:
```json
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码"
}
```

响应:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": "用户ID",
    "username": "用户名"
  }
}
```

#### 用户登录
```
POST /api/login
```

请求体:
```json
{
  "username": "用户名或邮箱",
  "password": "密码"
}
```

响应:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "JWT令牌",
    "user_id": "用户ID",
    "username": "用户名"
  }
}
```

### 需要认证的端点

以下端点需要在请求头中提供有效的JWT令牌。

#### 更新用户知识图谱
```
POST /api/knowledge-graph
```

请求体:
```json
{
  "knowledge_data": {
    // 知识图谱数据
  }
}
```

响应:
```json
{
  "success": true,
  "message": "知识图谱更新成功"
}
```

#### 获取用户知识图谱
```
GET /api/knowledge-graph
```

响应:
```json
{
  "success": true,
  "data": {
    "knowledge_graph": {
      // 知识图谱数据
    }
  }
}
```

#### 分析用户知识水平
```
POST /api/analyze-knowledge
```

请求体:
```json
{
  "answers": [
    // 用户答题数据
  ]
}
```

响应:
```json
{
  "success": true,
  "data": {
    "analysis": {
      // 分析结果
    }
  }
}
```

#### 获取学习主题推荐
```
GET /api/recommendations
```

响应:
```json
{
  "success": true,
  "data": [
    {
      "id": "machine_learning",
      "name": "机器学习基础",
      "key_points": ["监督学习", "无监督学习", "模型评估"]
    }
  ]
}
```

#### 生成个性化课程
```
POST /api/generate-lesson
```

请求体:
```json
{
  "learning_goal": "学习目标"
}
```

响应:
```json
{
  "success": true,
  "data": {
    "learning_goal": "学习目标",
    "content": {
      "explanation": "解释内容",
      "exercises": [
        // 练习题
      ]
    },
    "level": "用户水平"
  }
}
```

#### 完成课程记录
```
POST /api/complete-lesson
```

请求体:
```json
{
  "lesson_data": {
    // 课程完成数据
  }
}
```

响应:
```json
{
  "success": true,
  "message": "课程完成记录成功"
}
```

#### 获取学习进度
```
GET /api/progress
```

响应:
```json
{
  "success": true,
  "data": {
    "total_lessons_completed": 5,
    "completed_topics": 3,
    "recent_activity": [
      // 最近活动
    ],
    "weekly_activity": [1, 2, 0, 3, 1, 0, 2],
    "topic_mastery": {
      "python_basics": 0.8,
      "data_structures": 0.6
    },
    "knowledge_level": "beginner"
  }
}
```

#### 获取学习历史
```
GET /api/learning-history?page=1&per_page=10
```

查询参数:
- `page`: 页码，默认为1
- `per_page`: 每页数量，默认为10，最大100

响应:
```json
{
  "success": true,
  "message": "获取成功",
  "data": [
    // 学习历史记录
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

#### 生成个性化学习路径
```
POST /api/personalized-path
```

请求体:
```json
{
  "learning_goal": "学习目标"
}
```

响应:
```json
{
  "success": true,
  "data": {
    "user_id": "用户ID",
    "learning_goal": "学习目标",
    "user_level": "用户水平",
    "path": [
      {
        "topic": "主题",
        "explanation": "解释内容",
        "exercises": [
          // 练习题
        ],
        "estimated_time": 30,
        "prerequisites": [
          // 前置知识点
        ]
      }
    ]
  }
}
```

#### 处理练习反馈
```
POST /api/exercise-feedback
```

请求体:
```json
{
  "exercise_data": {
    "exercise_id": "练习ID",
    "type": "练习类型",
    "topic": "知识点",
    "user_answer": "用户答案",
    "correct_answer": "正确答案"
  }
}
```

响应:
```json
{
  "success": true,
  "data": {
    "user_id": "用户ID",
    "exercise_id": "练习ID",
    "score": 0.8,
    "topic_mastery": {
      "知识点": 0.75
    },
    "feedback_suggestion": {
      "score_level": "良好",
      "suggestions": [
        // 建议列表
      ],
      "next_steps": [
        // 下一步建议
      ]
    }
  }
}
```

#### 获取学习进度摘要
```
GET /api/progress-summary
```

响应:
```json
{
  "success": true,
  "data": {
    "total_lessons_completed": 12,
    "completed_topics": 8,
    "average_mastery": 0.75,
    "weekly_activity": [1, 2, 0, 3, 1, 0, 2],
    "knowledge_level": "intermediate",
    "recent_activity": [
      // 最近活动
    ]
  }
}
```

#### 获取学习报告
```
GET /api/learning-report
```

响应:
```json
{
  "success": true,
  "data": {
    "summary": {
      // 进度摘要
    },
    "charts": {
      "knowledge_map": "data:image/png;base64,...",  // 知识掌握情况图表
      "progress_timeline": "data:image/png;base64,...",  // 学习进度时间线图表
      "topic_mastery": "data:image/png;base64,..."  // 主题掌握情况图表
    }
  }
}
```

#### 获取特定主题的学习进度
```
GET /api/topic-progress/<topic>
```

响应:
```json
{
  "success": true,
  "data": {
    "topic": "主题名称",
    "mastery": 0.75,
    "time_spent": 120,
    "exercises_completed": 15,
    "accuracy": 0.8,
    "activities": [
      // 最近活动
    ]
  }
}
```

## 错误码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证或令牌无效
- `404`: 资源未找到
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 限流

为了保证服务稳定性，API可能实施请求限流。如果请求过于频繁，可能会收到`429 Too Many Requests`响应。

## 安全措施

- 使用JWT令牌进行认证
- 密码使用bcrypt加密存储
- 输入验证和清理防止XSS攻击
- 登录尝试次数限制防止暴力破解