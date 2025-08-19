"""
实时反馈处理器
用于即时评估学习效果并调整学习路径
"""

import random
from datetime import datetime
from utils.knowledge_analyzer import KnowledgeAnalyzer
from database import db
from bson import ObjectId

class FeedbackProcessor:
    """实时反馈处理器"""
    
    def __init__(self):
        """初始化反馈处理器"""
        self.knowledge_analyzer = KnowledgeAnalyzer()
    
    def process_exercise_feedback(self, user_id, exercise_data):
        """
        处理练习反馈
        
        Args:
            user_id (str): 用户ID
            exercise_data (dict): 练习数据
            
        Returns:
            dict: 反馈处理结果
        """
        # 计算练习得分
        score = self._calculate_exercise_score(exercise_data)
        
        # 分析知识点掌握情况
        topic_mastery = self._analyze_topic_mastery(exercise_data, score)
        
        # 更新用户知识图谱
        self._update_knowledge_graph(user_id, topic_mastery)
        
        # 生成反馈建议
        feedback_suggestion = self._generate_feedback_suggestion(score, topic_mastery)
        
        return {
            "user_id": user_id,
            "exercise_id": exercise_data.get('exercise_id'),
            "score": score,
            "topic_mastery": topic_mastery,
            "feedback_suggestion": feedback_suggestion,
            "processed_at": datetime.utcnow()
        }
    
    def _calculate_exercise_score(self, exercise_data):
        """
        计算练习得分
        
        Args:
            exercise_data (dict): 练习数据
            
        Returns:
            float: 得分 (0.0 - 1.0)
        """
        exercise_type = exercise_data.get('type')
        user_answer = exercise_data.get('user_answer')
        correct_answer = exercise_data.get('correct_answer')
        
        if exercise_type == 'multiple_choice':
            return 1.0 if user_answer == correct_answer else 0.0
        
        elif exercise_type == 'coding':
            # 简化的代码评估逻辑
            # 在实际应用中，这里可能需要集成代码评估引擎
            if user_answer and len(user_answer) > 10:
                return random.uniform(0.7, 1.0)  # 模拟评估结果
            else:
                return random.uniform(0.1, 0.5)
        
        elif exercise_type == 'conceptual':
            # 对于概念题，根据答案长度和关键词匹配评估
            if user_answer and len(user_answer) > 20:
                return random.uniform(0.6, 1.0)
            else:
                return random.uniform(0.1, 0.6)
        
        else:
            # 默认评估
            return 0.5
    
    def _analyze_topic_mastery(self, exercise_data, score):
        """
        分析知识点掌握情况
        
        Args:
            exercise_data (dict): 练习数据
            score (float): 练习得分
            
        Returns:
            dict: 知识点掌握情况
        """
        topic = exercise_data.get('topic', 'general')
        question = exercise_data.get('question', '')
        
        # 基于得分和题目内容分析知识点掌握情况
        mastery_level = score
        
        # 考虑题目的难度系数
        difficulty_factor = self._assess_question_difficulty(question)
        adjusted_mastery = mastery_level * difficulty_factor
        
        return {
            topic: min(1.0, max(0.0, adjusted_mastery)),
            "confidence": min(1.0, score * 1.2)  # 置信度基于得分但略高
        }
    
    def _assess_question_difficulty(self, question):
        """
        评估题目难度
        
        Args:
            question (str): 题目内容
            
        Returns:
            float: 难度系数 (0.8 - 1.2)
        """
        # 基于题目长度和关键词评估难度
        length_factor = min(1.2, 0.8 + len(question) / 100)
        
        # 关键词难度评估
        difficult_keywords = ['复杂', '高级', '优化', '实现', '设计', '算法']
        keyword_factor = 1.0
        for keyword in difficult_keywords:
            if keyword in question:
                keyword_factor += 0.1
        
        return min(1.2, length_factor * keyword_factor)
    
    def _update_knowledge_graph(self, user_id, topic_mastery):
        """
        更新用户知识图谱
        
        Args:
            user_id (str): 用户ID
            topic_mastery (dict): 知识点掌握情况
        """
        try:
            # 获取当前知识图谱
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            if not user:
                return
            
            knowledge_graph = user.get('knowledge_graph', {})
            
            # 更新知识点掌握情况
            for topic, mastery in topic_mastery.items():
                if topic != "confidence":
                    # 使用指数平滑更新掌握程度
                    current_mastery = knowledge_graph.get(topic, 0)
                    updated_mastery = 0.7 * current_mastery + 0.3 * mastery
                    knowledge_graph[topic] = round(updated_mastery, 2)
            
            # 更新知识图谱
            db.update_one(
                'users',
                {'_id': ObjectId(user_id)},
                {'knowledge_graph': knowledge_graph}
            )
            
        except Exception as e:
            print(f"更新知识图谱时出错: {e}")
    
    def _generate_feedback_suggestion(self, score, topic_mastery):
        """
        生成反馈建议
        
        Args:
            score (float): 练习得分
            topic_mastery (dict): 知识点掌握情况
            
        Returns:
            dict: 反馈建议
        """
        suggestions = []
        
        if score < 0.6:
            suggestions.append("您在这道题上遇到了困难，建议复习相关知识点")
            suggestions.append("可以尝试查看更基础的教程或示例")
        elif score < 0.8:
            suggestions.append("您基本掌握了知识点，但还有提升空间")
            suggestions.append("建议多做一些相关练习来巩固理解")
        else:
            suggestions.append("您很好地掌握了这个知识点！")
            suggestions.append("可以尝试挑战更高级的题目")
        
        # 基于知识点掌握情况的建议
        for topic, mastery in topic_mastery.items():
            if topic != "confidence":
                if mastery < 0.5:
                    suggestions.append(f"在{topic}方面还需要加强练习")
                elif mastery < 0.8:
                    suggestions.append(f"继续保持对{topic}的学习")
                else:
                    suggestions.append(f"您在{topic}方面表现优秀")
        
        return {
            "score_level": self._get_score_level(score),
            "suggestions": suggestions,
            "next_steps": self._suggest_next_steps(score)
        }
    
    def _get_score_level(self, score):
        """
        获取得分等级
        
        Args:
            score (float): 得分
            
        Returns:
            str: 得分等级
        """
        if score >= 0.9:
            return "优秀"
        elif score >= 0.8:
            return "良好"
        elif score >= 0.7:
            return "中等"
        elif score >= 0.6:
            return "及格"
        else:
            return "需要改进"
    
    def _suggest_next_steps(self, score):
        """
        建议下一步行动
        
        Args:
            score (float): 得分
            
        Returns:
            list: 下一步行动建议
        """
        if score < 0.6:
            return ["复习相关概念", "查看解题思路", "寻求帮助"]
        elif score < 0.8:
            return ["做更多练习题", "查看详细解析", "与他人讨论"]
        else:
            return ["挑战更高难度题目", "学习相关高级内容", "帮助其他学习者"]
    
    def process_learning_session_feedback(self, user_id, session_data):
        """
        处理学习会话反馈
        
        Args:
            user_id (str): 用户ID
            session_data (dict): 学习会话数据
            
        Returns:
            dict: 会话反馈处理结果
        """
        # 计算会话整体表现
        exercises = session_data.get('exercises', [])
        total_score = sum(self._calculate_exercise_score(ex) for ex in exercises)
        average_score = total_score / len(exercises) if exercises else 0
        
        # 分析会话中的知识点掌握情况
        session_mastery = {}
        for exercise in exercises:
            exercise_score = self._calculate_exercise_score(exercise)
            topic_mastery = self._analyze_topic_mastery(exercise, exercise_score)
            for topic, mastery in topic_mastery.items():
                if topic != "confidence":
                    if topic in session_mastery:
                        session_mastery[topic].append(mastery)
                    else:
                        session_mastery[topic] = [mastery]
        
        # 计算平均掌握程度
        avg_mastery = {}
        for topic, mastery_list in session_mastery.items():
            avg_mastery[topic] = sum(mastery_list) / len(mastery_list)
        
        # 更新知识图谱
        self._update_knowledge_graph(user_id, avg_mastery)
        
        # 生成会话反馈
        session_feedback = self._generate_session_feedback(average_score, avg_mastery, session_data)
        
        return {
            "user_id": user_id,
            "session_id": session_data.get('session_id'),
            "average_score": average_score,
            "topic_mastery": avg_mastery,
            "feedback": session_feedback,
            "processed_at": datetime.utcnow()
        }
    
    def _generate_session_feedback(self, average_score, topic_mastery, session_data):
        """
        生成会话反馈
        
        Args:
            average_score (float): 平均得分
            topic_mastery (dict): 知识点掌握情况
            session_data (dict): 会话数据
            
        Returns:
            dict: 会话反馈
        """
        feedback = {
            "overall_performance": self._get_score_level(average_score),
            "time_spent": session_data.get('time_spent', 0),
            "exercises_completed": len(session_data.get('exercises', []))
        }
        
        # 强项和弱项分析
        strengths = []
        weaknesses = []
        
        for topic, mastery in topic_mastery.items():
            if mastery >= 0.8:
                strengths.append(topic)
            elif mastery <= 0.5:
                weaknesses.append(topic)
        
        feedback["strengths"] = strengths
        feedback["weaknesses"] = weaknesses
        
        # 学习建议
        suggestions = []
        if average_score < 0.6:
            suggestions.append("本次学习效果不太理想，建议放慢节奏，确保理解每个概念")
        elif average_score < 0.8:
            suggestions.append("学习效果不错，继续保持并加强薄弱环节的练习")
        else:
            suggestions.append("学习效果优秀，可以尝试挑战更高难度的内容")
        
        if weaknesses:
            suggestions.append(f"重点关注以下知识点: {', '.join(weaknesses)}")
        
        feedback["suggestions"] = suggestions
        
        return feedback