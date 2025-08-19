"""
学习路径规划器
根据用户知识水平定制学习内容和路径
"""

import random
from datetime import datetime, timedelta
from utils.knowledge_analyzer import KnowledgeAnalyzer
from utils.content_generator import ContentGenerator

class LearningPathPlanner:
    """学习路径规划器"""
    
    def __init__(self):
        """初始化学习路径规划器"""
        self.knowledge_analyzer = KnowledgeAnalyzer()
        self.content_generator = ContentGenerator()
        
        # 定义学习路径规则
        self.learning_paths = {
            "python_basics": {
                "beginner": ["variables", "data_types", "control_structures", "functions"],
                "intermediate": ["decorators", "generators", "context_managers", "modules"],
                "advanced": ["memory_management", "performance_optimization", "cython_integration"]
            },
            "data_structures": {
                "beginner": ["arrays", "lists", "stacks", "queues"],
                "intermediate": ["trees", "graphs", "hash_tables", "heaps"],
                "advanced": ["advanced_trees", "graph_algorithms", "distributed_structures"]
            },
            "web_development": {
                "beginner": ["html_basics", "css_basics", "javascript_fundamentals"],
                "intermediate": ["dom_manipulation", "ajax", "frontend_frameworks"],
                "advanced": ["ssr", "ssg", "web_security", "performance_optimization"]
            },
            "machine_learning": {
                "beginner": ["supervised_learning", "unsupervised_learning", "model_evaluation"],
                "intermediate": ["neural_networks", "feature_engineering", "cross_validation"],
                "advanced": ["deep_learning", "ensemble_methods", "hyperparameter_optimization"]
            }
        }
    
    def generate_personalized_learning_path(self, user_id, knowledge_graph, learning_goal):
        """
        生成个性化学习路径
        
        Args:
            user_id (str): 用户ID
            knowledge_graph (dict): 用户知识图谱
            learning_goal (str): 学习目标
            
        Returns:
            dict: 个性化学习路径
        """
        # 分析用户水平
        level_analysis = self.knowledge_analyzer.analyze_user_level(knowledge_graph)
        user_level = level_analysis.get('level', 'beginner')
        
        # 获取学习目标对应的学习路径
        if learning_goal not in self.learning_paths:
            learning_goal = "python_basics"  # 默认学习目标
        
        path = self.learning_paths[learning_goal].get(user_level, [])
        
        # 生成学习路径详情
        learning_path_details = []
        for topic in path:
            # 获取相关学习材料
            materials = self.content_generator.retrieve_materials(learning_goal, level_analysis)
            explanation = self.content_generator.generate_explanation(level_analysis, materials, knowledge_graph)
            exercises = self.content_generator.generate_exercises(level_analysis, materials)
            
            learning_path_details.append({
                "topic": topic,
                "explanation": explanation,
                "exercises": exercises,
                "estimated_time": self._estimate_learning_time(topic, user_level),
                "prerequisites": self._get_prerequisites(learning_goal, topic)
            })
        
        return {
            "user_id": user_id,
            "learning_goal": learning_goal,
            "user_level": user_level,
            "path": learning_path_details,
            "generated_at": datetime.utcnow()
        }
    
    def _estimate_learning_time(self, topic, user_level):
        """
        估算学习时间
        
        Args:
            topic (str): 学习主题
            user_level (str): 用户水平
            
        Returns:
            int: 估算时间（分钟）
        """
        base_time = {
            "variables": 15,
            "data_types": 20,
            "control_structures": 25,
            "functions": 30,
            "decorators": 40,
            "generators": 35,
            "context_managers": 30,
            "modules": 25,
            "memory_management": 50,
            "performance_optimization": 60,
            "cython_integration": 70
        }
        
        time_multiplier = {
            "beginner": 1.0,
            "intermediate": 1.2,
            "advanced": 1.5
        }
        
        base = base_time.get(topic, 30)
        multiplier = time_multiplier.get(user_level, 1.0)
        
        return int(base * multiplier)
    
    def _get_prerequisites(self, learning_goal, topic):
        """
        获取前置知识点
        
        Args:
            learning_goal (str): 学习目标
            topic (str): 学习主题
            
        Returns:
            list: 前置知识点列表
        """
        prerequisites_map = {
            "functions": ["variables", "data_types"],
            "decorators": ["functions"],
            "generators": ["functions"],
            "context_managers": ["functions"],
            "neural_networks": ["supervised_learning"],
            "feature_engineering": ["supervised_learning"],
            "cross_validation": ["model_evaluation"],
            "deep_learning": ["neural_networks"],
            "ensemble_methods": ["supervised_learning"],
            "frontend_frameworks": ["javascript_fundamentals"],
            "ssr": ["frontend_frameworks"],
            "ssg": ["frontend_frameworks"],
            "web_security": ["frontend_frameworks"]
        }
        
        return prerequisites_map.get(topic, [])
    
    def adapt_learning_path(self, user_id, learning_path, feedback_data):
        """
        根据用户反馈调整学习路径
        
        Args:
            user_id (str): 用户ID
            learning_path (dict): 当前学习路径
            feedback_data (dict): 用户反馈数据
            
        Returns:
            dict: 调整后的学习路径
        """
        # 分析用户反馈
        difficulty_rating = feedback_data.get('difficulty', 3)  # 1-5分
        interest_rating = feedback_data.get('interest', 3)     # 1-5分
        time_spent = feedback_data.get('time_spent', 0)        # 分钟
        
        # 根据反馈调整路径
        adapted_path = learning_path.copy()
        
        # 如果用户觉得太难，插入复习内容
        if difficulty_rating >= 4:
            adapted_path = self._add_review_content(adapted_path)
        
        # 如果用户觉得太简单，跳过部分内容
        if difficulty_rating <= 2:
            adapted_path = self._skip_basic_content(adapted_path)
        
        # 根据兴趣调整内容重点
        if interest_rating >= 4:
            adapted_path = self._emphasize_interesting_content(adapted_path, feedback_data.get('preferred_topics', []))
        
        adapted_path['adapted_at'] = datetime.utcnow()
        adapted_path['adaptation_reason'] = feedback_data
        
        return adapted_path
    
    def _add_review_content(self, learning_path):
        """
        添加复习内容
        
        Args:
            learning_path (dict): 学习路径
            
        Returns:
            dict: 添加了复习内容的学习路径
        """
        # 在路径开始添加复习内容
        review_content = {
            "topic": "review",
            "explanation": "根据您的反馈，我们为您添加了复习内容以巩固基础知识",
            "exercises": [
                {
                    "type": "conceptual",
                    "question": "请总结您已学过的知识点",
                    "answer": "开放性问题"
                }
            ],
            "estimated_time": 20,
            "prerequisites": []
        }
        
        learning_path['path'].insert(0, review_content)
        return learning_path
    
    def _skip_basic_content(self, learning_path):
        """
        跳过基础内容
        
        Args:
            learning_path (dict): 学习路径
            
        Returns:
            dict: 跳过了基础内容的学习路径
        """
        # 移除前几个基础内容
        if len(learning_path['path']) > 3:
            learning_path['path'] = learning_path['path'][2:]
        
        return learning_path
    
    def _emphasize_interesting_content(self, learning_path, preferred_topics):
        """
        强调用户感兴趣的内容
        
        Args:
            learning_path (dict): 学习路径
            preferred_topics (list): 用户偏好的主题
            
        Returns:
            dict: 强调了感兴趣内容的学习路径
        """
        # 为用户偏好的主题添加更多练习
        for item in learning_path['path']:
            if item['topic'] in preferred_topics:
                # 添加额外练习
                extra_exercises = [
                    {
                        "type": "coding",
                        "question": f"关于{item['topic']}的额外练习题",
                        "answer": "根据具体主题而定"
                    }
                ]
                item['exercises'].extend(extra_exercises)
                item['estimated_time'] += 15
        
        return learning_path