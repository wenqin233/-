"""
知识分析工具模块
用于分析用户知识水平和生成个性化学习内容
"""

import random
from datetime import datetime, timedelta

class KnowledgeAnalyzer:
    """知识分析器"""
    
    def __init__(self):
        """初始化知识分析器"""
        # 定义知识点权重，用于计算综合水平
        self.topic_weights = {
            'python_basics': 0.3,
            'data_structures': 0.2,
            'web_development': 0.2,
            'machine_learning': 0.3
        }
        
        # 定义水平阈值
        self.level_thresholds = {
            'beginner': 0.3,
            'intermediate': 0.7,
            'advanced': 1.0
        }
    
    def analyze_user_level(self, knowledge_graph):
        """
        分析用户知识水平
        
        Args:
            knowledge_graph (dict): 用户知识图谱
            
        Returns:
            dict: 包含用户水平和最佳挑战级别的分析结果
        """
        # 如果知识图谱为空，返回初学者水平
        if not knowledge_graph:
            return {
                "level": "beginner",
                "optimal_challenge": "easy",
                "confidence": 0.0
            }
        
        # 获取用户的综合知识水平
        overall_level = self._calculate_overall_level(knowledge_graph)
        
        # 确定用户水平
        level = self._determine_level(overall_level)
        
        # 确定最优挑战级别
        optimal_challenge = self._determine_optimal_challenge(level)
        
        return {
            "level": level,
            "optimal_challenge": optimal_challenge,
            "confidence": overall_level
        }
    
    def _calculate_overall_level(self, knowledge_graph):
        """
        计算用户的综合知识水平
        
        Args:
            knowledge_graph (dict): 用户知识图谱
            
        Returns:
            float: 综合知识水平 (0.0 - 1.0)
        """
        if not knowledge_graph:
            return 0.0
        
        # 如果有直接的水平信息，使用它
        if 'level' in knowledge_graph:
            level_str = knowledge_graph['level']
            if level_str == 'beginner':
                return 0.2
            elif level_str == 'intermediate':
                return 0.5
            elif level_str == 'advanced':
                return 0.8
        
        # 基于知识点掌握情况计算综合水平
        total_weight = 0.0
        weighted_score = 0.0
        
        for topic, weight in self.topic_weights.items():
            if topic in knowledge_graph:
                # 假设知识点的值在0-1之间表示掌握程度
                mastery = knowledge_graph[topic] if isinstance(knowledge_graph[topic], (int, float)) else 0.5
                mastery = max(0.0, min(1.0, mastery))  # 确保在有效范围内
                
                weighted_score += mastery * weight
                total_weight += weight
        
        # 如果没有匹配的知识点，返回默认值
        if total_weight == 0.0:
            return 0.0
        
        return weighted_score / total_weight
    
    def _determine_level(self, overall_level):
        """
        根据综合水平确定用户水平
        
        Args:
            overall_level (float): 综合知识水平
            
        Returns:
            str: 用户水平 (beginner, intermediate, advanced)
        """
        if overall_level <= self.level_thresholds['beginner']:
            return 'beginner'
        elif overall_level <= self.level_thresholds['intermediate']:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _determine_optimal_challenge(self, level):
        """
        根据用户水平确定最优挑战级别
        
        Args:
            level (str): 用户水平
            
        Returns:
            str: 最优挑战级别 (easy, medium, hard)
        """
        if level == 'beginner':
            return 'easy'
        elif level == 'intermediate':
            return 'medium'
        else:
            return 'hard'
    
    def assess_knowledge_by_questions(self, answers):
        """
        通过问题回答评估知识水平
        
        Args:
            answers (list): 用户答案列表
            
        Returns:
            dict: 知识水平评估结果
        """
        # 统计正确率
        correct_count = sum(1 for answer in answers if answer.get('correct', False))
        total_count = len(answers)
        
        # 简单分级
        if total_count == 0:
            level = "beginner"
            accuracy = 0
        else:
            accuracy = correct_count / total_count
            if accuracy >= 0.8:
                level = "advanced"
            elif accuracy >= 0.5:
                level = "intermediate"
            else:
                level = "beginner"
        
        # 生成知识点掌握情况
        knowledge_points = self._generate_knowledge_points(answers, accuracy)
        
        return {
            "level": level,
            "correct_count": correct_count,
            "total_count": total_count,
            "accuracy": accuracy,
            "knowledge_points": knowledge_points
        }
    
    def _generate_knowledge_points(self, answers, accuracy):
        """
        根据答题情况生成知识点掌握情况
        
        Args:
            answers (list): 用户答案列表
            accuracy (float): 答题准确率
            
        Returns:
            dict: 知识点掌握情况
        """
        # 简化的知识点生成逻辑
        # 在实际应用中，这里会根据具体题目分析涉及的知识点
        knowledge_points = {}
        
        # 随机选择一些知识点并根据准确率设置掌握程度
        topics = list(self.topic_weights.keys())
        num_topics = random.randint(1, len(topics))
        selected_topics = random.sample(topics, num_topics)
        
        for topic in selected_topics:
            # 根据准确率和一些随机因素确定掌握程度
            base_mastery = accuracy
            variation = random.uniform(-0.1, 0.1)
            mastery = max(0.0, min(1.0, base_mastery + variation))
            knowledge_points[topic] = round(mastery, 2)
        
        return knowledge_points
    
    def recommend_next_topics(self, knowledge_graph, num_recommendations=3):
        """
        推荐下一步学习的主题
        
        Args:
            knowledge_graph (dict): 用户知识图谱
            num_recommendations (int): 推荐主题数量
            
        Returns:
            list: 推荐的主题列表
        """
        # 获取所有可能的主题
        all_topics = list(self.topic_weights.keys())
        
        # 找出用户尚未掌握或掌握程度较低的主题
        weak_topics = []
        for topic in all_topics:
            mastery = knowledge_graph.get(topic, 0) if isinstance(knowledge_graph, dict) else 0
            if mastery < 0.7:  # 掌握程度低于70%的主题需要加强
                weak_topics.append((topic, mastery))
        
        # 按掌握程度排序，优先推荐掌握程度最低的主题
        weak_topics.sort(key=lambda x: x[1])
        
        # 如果掌握程度低的主题不足，添加一些未学习过的主题
        if len(weak_topics) < num_recommendations:
            studied_topics = set(knowledge_graph.keys()) if isinstance(knowledge_graph, dict) else set()
            unstudied_topics = [topic for topic in all_topics if topic not in studied_topics and topic not in ['level', 'updated_at']]
            
            # 添加未学习的主题
            for topic in unstudied_topics:
                weak_topics.append((topic, 0))
        
        # 返回推荐的主题
        return [topic for topic, mastery in weak_topics[:num_recommendations]]