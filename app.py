from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import logging
from functools import wraps

from config import config
from database import db
from auth import Auth
from progress_tracker import ProgressTracker
from utils.knowledge_analyzer import KnowledgeAnalyzer
from utils.content_generator import ContentGenerator
from utils.validators import validate_request
from utils.response import ResponseUtil
from utils.paginator import Paginator
from utils.learning_path_planner import LearningPathPlanner
from utils.feedback_processor import FeedbackProcessor
from utils.progress_visualizer import ProgressVisualizer
from logging_config import setup_logging, get_logger

# 创建Flask应用实例
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# 加载配置
config_name = os.getenv('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])

# 初始化CORS
CORS(app)

# 初始化工具类
knowledge_analyzer = KnowledgeAnalyzer()
content_generator = ContentGenerator()
progress_tracker = ProgressTracker()

# 初始化新工具类
learning_path_planner = LearningPathPlanner()
feedback_processor = FeedbackProcessor()
progress_visualizer = ProgressVisualizer()

# 设置日志
setup_logging(app)
logger = get_logger(__name__)

def token_required(f):
    """
    装饰器：验证JWT令牌
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取令牌
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return ResponseUtil.error('令牌格式无效', 401)
        
        if not token:
            return ResponseUtil.error('缺少访问令牌', 401)
        
        # 验证令牌
        result = Auth.verify_token(token)
        if not result['success']:
            return ResponseUtil.error(result['message'], 401)
        
        # 将用户信息添加到请求上下文
        request.user_id = result['user_id']
        request.username = result['username']
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/')
def home():
    """主页面"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """用户仪表板"""
    return render_template('dashboard.html')

@app.route('/lesson')
def lesson():
    """课程详情页面"""
    return render_template('lesson.html')

@app.route('/exercise')
def exercise():
    """练习页面"""
    return render_template('exercise.html')

@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')

@app.route('/docs')
def docs():
    """API文档页面"""
    return render_template('docs.html')

@app.route('/health')
def health_check():
    """健康检查端点"""
    logger.info("健康检查请求")
    return ResponseUtil.success({
        "status": "healthy", 
        "service": "AI个性化学习伴侣"
    })

@app.route('/api/register', methods=['POST'])
@validate_request({
    'username': {
        'required': True,
        'type': 'string',
        'min_length': 3,
        'max_length': 30
    },
    'email': {
        'required': True,
        'type': 'email'
    },
    'password': {
        'required': True,
        'type': 'string',
        'min_length': 8,
        'max_length': 128
    }
})
def register():
    """用户注册"""
    try:
        username = request.validated_data.get('username')
        email = request.validated_data.get('email')
        password = request.validated_data.get('password')
        
        result = Auth.register_user(username, email, password)
        if result['success']:
            logger.info(f"用户注册成功: {username}")
            return ResponseUtil.success({
                'user_id': result['user_id'],
                'username': result['username']
            }, result['message'], 201)
        else:
            logger.warning(f"用户注册失败: {result['message']}")
            return ResponseUtil.error(result['message'], 400)
            
    except Exception as e:
        logger.error(f"注册过程中出错: {str(e)}")
        return ResponseUtil.error("注册失败")

@app.route('/api/login', methods=['POST'])
@validate_request({
    'username': {
        'required': True,
        'type': 'string',
        'min_length': 1,
        'max_length': 128
    },
    'password': {
        'required': True,
        'type': 'string',
        'min_length': 1,
        'max_length': 128
    }
})
def login():
    """用户登录"""
    try:
        username = request.validated_data.get('username')
        password = request.validated_data.get('password')
        
        # 获取客户端IP地址
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        
        result = Auth.authenticate_user(username, password, ip_address)
        if result['success']:
            logger.info(f"用户登录成功: {username}")
            return ResponseUtil.success({
                'user_id': result['user_id'],
                'username': result['username']
            }, result['message'])
        else:
            logger.warning(f"用户登录失败: {result['message']}")
            return ResponseUtil.error(result['message'], 401)
            
    except Exception as e:
        logger.error(f"登录过程中出错: {str(e)}")
        return ResponseUtil.error("登录失败")

@app.route('/api/knowledge-graph', methods=['POST'])
@token_required
@validate_request({
    'knowledge_data': {
        'required': True,
        'type': 'object'
    }
})
def update_knowledge_graph():
    """更新用户知识图谱"""
    try:
        knowledge_data = request.validated_data.get('knowledge_data')
        
        success = progress_tracker.update_knowledge_graph(request.user_id, knowledge_data)
        if success:
            logger.info(f"用户 {request.username} 知识图谱更新成功")
            return ResponseUtil.success(message="知识图谱更新成功")
        else:
            logger.error(f"用户 {request.username} 知识图谱更新失败")
            return ResponseUtil.error("知识图谱更新失败")
            
    except Exception as e:
        logger.error(f"更新知识图谱时出错: {str(e)}")
        return ResponseUtil.error("更新失败")

@app.route('/api/knowledge-graph', methods=['GET'])
@token_required
def get_knowledge_graph():
    """获取用户知识图谱"""
    try:
        knowledge_graph = progress_tracker.get_knowledge_graph(request.user_id)
        logger.info(f"获取用户 {request.username} 知识图谱成功")
        return ResponseUtil.success({'knowledge_graph': knowledge_graph})
        
    except Exception as e:
        logger.error(f"获取知识图谱时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/analyze-knowledge', methods=['POST'])
@token_required
@validate_request({
    'answers': {
        'required': True,
        'type': 'array'
    }
})
def analyze_knowledge():
    """分析用户知识水平"""
    try:
        answers = request.validated_data.get('answers')
        
        # 基于用户答案分析知识水平
        analysis = knowledge_analyzer.assess_knowledge_by_questions(answers)
        
        # 更新用户知识图谱
        progress_tracker.update_knowledge_graph(request.user_id, analysis)
        
        logger.info(f"用户 {request.username} 知识水平分析完成")
        return ResponseUtil.success({'analysis': analysis})
        
    except Exception as e:
        logger.error(f"分析知识水平时出错: {str(e)}")
        return ResponseUtil.error("分析失败")

@app.route('/api/generate-lesson', methods=['POST'])
@token_required
@validate_request({
    'learning_goal': {
        'required': True,
        'type': 'string',
        'min_length': 1,
        'max_length': 100
    }
})
def generate_lesson():
    """生成个性化课程内容"""
    try:
        learning_goal = request.validated_data.get('learning_goal')
        
        # 获取用户知识图谱
        user_knowledge_graph = progress_tracker.get_knowledge_graph(request.user_id)
        
        # 分析用户水平
        level_analysis = knowledge_analyzer.analyze_user_level(user_knowledge_graph)
        
        # 检索学习材料
        materials = content_generator.retrieve_materials(learning_goal, level_analysis)
        
        if not materials:
            logger.warning(f"未找到学习目标 '{learning_goal}' 的相关材料")
            return ResponseUtil.error("未找到相关学习材料", 404)
        
        # 生成解释内容
        explanation = content_generator.generate_explanation(level_analysis, materials, user_knowledge_graph)
        
        # 生成练习题
        exercises = content_generator.generate_exercises(level_analysis, materials)
        
        # 构建课程数据
        lesson_data = {
            "learning_goal": learning_goal,
            "content": {
                "explanation": explanation,
                "exercises": exercises
            },
            "level": level_analysis.get('level', 'beginner')
        }
        
        logger.info(f"为用户 {request.username} 生成课程 '{learning_goal}' 成功")
        return ResponseUtil.success(lesson_data)
        
    except Exception as e:
        logger.error(f"生成课程时出错: {str(e)}")
        return ResponseUtil.error("生成失败")

@app.route('/api/complete-lesson', methods=['POST'])
@token_required
@validate_request({
    'lesson_data': {
        'required': True,
        'type': 'object'
    }
})
def complete_lesson():
    """完成课程"""
    try:
        lesson_data = request.validated_data.get('lesson_data')
        
        # 添加学习历史记录
        success = progress_tracker.add_learning_history(request.user_id, lesson_data)
        
        if success:
            logger.info(f"用户 {request.username} 完成课程记录成功")
            return ResponseUtil.success(message="课程完成记录成功")
        else:
            logger.error(f"用户 {request.username} 完成课程记录失败")
            return ResponseUtil.error("记录失败")
            
    except Exception as e:
        logger.error(f"记录完成课程时出错: {str(e)}")
        return ResponseUtil.error("记录失败")

@app.route('/api/progress', methods=['GET'])
@token_required
def get_progress():
    """获取学习进度"""
    try:
        progress_summary = progress_tracker.get_user_progress_summary(request.user_id)
        logger.info(f"获取用户 {request.username} 学习进度成功")
        return ResponseUtil.success(progress_summary)
        
    except Exception as e:
        logger.error(f"获取学习进度时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/learning-history', methods=['GET'])
@token_required
def get_learning_history():
    """获取学习历史（支持分页）"""
    try:
        # 获取分页参数
        paginator = Paginator()
        
        # 获取学习历史和总数
        history, total = progress_tracker.get_learning_history_with_count(
            request.user_id, 
            paginator.per_page, 
            paginator.get_offset()
        )
        
        logger.info(f"获取用户 {request.username} 学习历史成功")
        return ResponseUtil.paginated(
            history, 
            paginator.page, 
            paginator.per_page, 
            total
        )
        
    except Exception as e:
        logger.error(f"获取学习历史时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """获取所有可用的学习主题"""
    try:
        topics = content_generator.get_available_topics()
        topic_info_list = []
        
        for topic in topics:
            topic_info = content_generator.get_topic_info(topic)
            if topic_info:
                topic_info_list.append({
                    "id": topic,
                    "name": topic_info["concept"],
                    "key_points": topic_info["key_points"]
                })
        
        logger.info("获取学习主题列表成功")
        return ResponseUtil.success(topic_info_list)
        
    except Exception as e:
        logger.error(f"获取学习主题列表时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations():
    """获取学习主题推荐"""
    try:
        # 获取用户知识图谱
        knowledge_graph = progress_tracker.get_knowledge_graph(request.user_id)
        
        # 获取推荐主题
        recommendations = knowledge_analyzer.recommend_next_topics(knowledge_graph)
        
        # 获取推荐主题的详细信息
        recommended_topics = []
        for topic in recommendations:
            topic_info = content_generator.get_topic_info(topic)
            if topic_info:
                recommended_topics.append({
                    "id": topic,
                    "name": topic_info["concept"],
                    "key_points": topic_info["key_points"]
                })
        
        logger.info(f"为用户 {request.username} 生成主题推荐成功")
        return ResponseUtil.success(recommended_topics)
        
    except Exception as e:
        logger.error(f"生成主题推荐时出错: {str(e)}")
        return ResponseUtil.error("推荐失败")

@app.route('/api/personalized-path', methods=['POST'])
@token_required
@validate_request({
    'learning_goal': {
        'required': True,
        'type': 'string',
        'min_length': 1,
        'max_length': 50
    }
})
def generate_personalized_path():
    """生成个性化学习路径"""
    try:
        learning_goal = request.validated_data.get('learning_goal')
        
        # 获取用户知识图谱
        knowledge_graph = progress_tracker.get_knowledge_graph(request.user_id)
        
        # 生成个性化学习路径
        learning_path = learning_path_planner.generate_personalized_learning_path(
            request.user_id, 
            knowledge_graph, 
            learning_goal
        )
        
        logger.info(f"为用户 {request.username} 生成个性化学习路径成功")
        return ResponseUtil.success(learning_path)
        
    except Exception as e:
        logger.error(f"生成个性化学习路径时出错: {str(e)}")
        return ResponseUtil.error("生成失败")

@app.route('/api/exercise-feedback', methods=['POST'])
@token_required
@validate_request({
    'exercise_data': {
        'required': True,
        'type': 'dict'
    }
})
def process_exercise_feedback():
    """处理练习反馈"""
    try:
        exercise_data = request.validated_data.get('exercise_data')
        
        # 处理练习反馈
        feedback_result = feedback_processor.process_exercise_feedback(
            request.user_id, 
            exercise_data
        )
        
        logger.info(f"处理用户 {request.username} 的练习反馈成功")
        return ResponseUtil.success(feedback_result)
        
    except Exception as e:
        logger.error(f"处理练习反馈时出错: {str(e)}")
        return ResponseUtil.error("处理失败")

@app.route('/api/progress-summary', methods=['GET'])
@token_required
def get_progress_summary():
    """获取学习进度摘要"""
    try:
        # 获取进度摘要
        summary = progress_visualizer.get_progress_summary(request.user_id)
        
        logger.info(f"获取用户 {request.username} 的进度摘要成功")
        return ResponseUtil.success(summary)
        
    except Exception as e:
        logger.error(f"获取进度摘要时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/learning-report', methods=['GET'])
@token_required
def get_learning_report():
    """获取学习报告"""
    try:
        # 生成学习报告
        report = progress_visualizer.generate_learning_report(request.user_id)
        
        logger.info(f"生成用户 {request.username} 的学习报告成功")
        return ResponseUtil.success(report)
        
    except Exception as e:
        logger.error(f"生成学习报告时出错: {str(e)}")
        return ResponseUtil.error("生成失败")

@app.route('/api/topic-progress/<topic>', methods=['GET'])
@token_required
def get_topic_progress(topic):
    """获取特定主题的学习进度"""
    try:
        # 获取主题进度
        topic_progress = progress_visualizer.get_topic_progress(request.user_id, topic)
        
        logger.info(f"获取用户 {request.username} 的主题 {topic} 进度成功")
        return ResponseUtil.success(topic_progress)
        
    except Exception as e:
        logger.error(f"获取主题进度时出错: {str(e)}")
        return ResponseUtil.error("获取失败")

@app.route('/api/interactive-chat', methods=['POST'])
@validate_request({
    'message': {
        'required': True,
        'type': 'string',
        'min_length': 1,
        'max_length': 1000
    },
    'context': {
        'required': False,
        'type': 'dict'
    },
    'topic': {
        'required': False,
        'type': 'string'
    }
})
def interactive_chat():
    """处理交互式对话学习请求"""
    try:
        message = request.validated_data.get('message')
        context = request.validated_data.get('context', {})
        topic = request.validated_data.get('topic', 'general')
        
        # 获取用户ID（如果已登录）
        user_id = getattr(request, 'user_id', None)
        
        # 获取用户知识图谱（如果用户已登录）
        knowledge_graph = {}
        if user_id:
            knowledge_graph = progress_tracker.get_knowledge_graph(user_id)
        
        # 使用内容生成器生成响应
        response = content_generator.generate_interactive_response(
            message, 
            context, 
            topic, 
            knowledge_graph
        )
        
        if response:
            logger.info("交互式对话响应生成成功")
            return ResponseUtil.success({
                'response': response,
                'context': context
            })
        else:
            logger.warning("交互式对话响应生成失败")
            return ResponseUtil.error("无法生成响应，请稍后重试")
            
    except Exception as e:
        logger.error(f"处理交互式对话时出错: {str(e)}")
        return ResponseUtil.error("处理对话时发生错误")

# 404错误处理
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"页面未找到: {request.url}")
    return ResponseUtil.error("页面未找到", 404)

# 全局错误处理
@app.errorhandler(Exception)
def internal_error(error):
    logger.error(f"服务器内部错误: {str(error)}")
    return ResponseUtil.error("服务器内部错误")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))