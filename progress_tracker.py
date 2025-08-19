"""
学习进度跟踪模块
用于跟踪和管理用户学习进度
"""

from database import db
import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """学习进度跟踪类"""
    
    @staticmethod
    def update_knowledge_graph(user_id, knowledge_data):
        """
        更新用户知识图谱
        
        Args:
            user_id (str): 用户ID
            knowledge_data (dict): 知识图谱数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 添加更新时间戳
            knowledge_data['updated_at'] = datetime.datetime.utcnow()
            
            result = db.update_one(
                'users', 
                {'_id': ObjectId(user_id)}, 
                {'knowledge_graph': knowledge_data}
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"用户 {user_id} 知识图谱更新成功")
            else:
                logger.warning(f"用户 {user_id} 知识图谱无变化或更新失败")
            return success
        except Exception as e:
            logger.error(f"更新知识图谱失败: {e}")
            return False
    
    @staticmethod
    def get_knowledge_graph(user_id):
        """
        获取用户知识图谱
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 知识图谱数据
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            knowledge_graph = user.get('knowledge_graph', {}) if user else {}
            logger.debug(f"获取用户 {user_id} 知识图谱成功")
            return knowledge_graph
        except Exception as e:
            logger.error(f"获取知识图谱失败: {e}")
            return {}
    
    @staticmethod
    def add_learning_history(user_id, lesson_data):
        """
        添加学习历史记录
        
        Args:
            user_id (str): 用户ID
            lesson_data (dict): 课程数据
            
        Returns:
            bool: 添加是否成功
        """
        try:
            # 添加时间戳
            lesson_data['completed_at'] = datetime.datetime.utcnow()
            
            result = db.update_one(
                'users',
                {'_id': ObjectId(user_id)},
                {'$push': {'learning_history': lesson_data}}
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"用户 {user_id} 学习历史添加成功")
            else:
                logger.warning(f"用户 {user_id} 学习历史添加失败")
            return success
        except Exception as e:
            logger.error(f"添加学习历史失败: {e}")
            return False
    
    @staticmethod
    def get_learning_history(user_id, limit=10, skip=0):
        """
        获取用户学习历史
        
        Args:
            user_id (str): 用户ID
            limit (int): 限制返回记录数
            skip (int): 跳过记录数
            
        Returns:
            list: 学习历史记录列表
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            history = user.get('learning_history', []) if user else []
            
            # 按时间倒序排列
            history.sort(key=lambda x: x.get('completed_at', datetime.datetime.min), reverse=True)
            
            # 应用分页
            paginated_history = history[skip:skip+limit] if limit > 0 else history[skip:]
            
            logger.debug(f"获取用户 {user_id} 学习历史成功，返回 {len(paginated_history)} 条记录")
            return paginated_history
        except Exception as e:
            logger.error(f"获取学习历史失败: {e}")
            return []
    
    @staticmethod
    def get_learning_history_with_count(user_id, limit=10, skip=0):
        """
        获取用户学习历史和总数（用于分页）
        
        Args:
            user_id (str): 用户ID
            limit (int): 限制返回记录数
            skip (int): 跳过记录数
            
        Returns:
            tuple: (学习历史记录列表, 总数)
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            history = user.get('learning_history', []) if user else []
            
            # 按时间倒序排列
            history.sort(key=lambda x: x.get('completed_at', datetime.datetime.min), reverse=True)
            
            # 应用分页
            paginated_history = history[skip:skip+limit] if limit > 0 else history[skip:]
            total = len(history)
            
            logger.debug(f"获取用户 {user_id} 学习历史成功，返回 {len(paginated_history)} 条记录，总共 {total} 条")
            return paginated_history, total
        except Exception as e:
            logger.error(f"获取学习历史失败: {e}")
            return [], 0
    
    @staticmethod
    def get_user_progress_summary(user_id):
        """
        获取用户学习进度摘要
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 进度摘要
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            if not user:
                logger.warning(f"获取用户进度摘要失败: 用户 {user_id} 不存在")
                return {}
            
            knowledge_graph = user.get('knowledge_graph', {})
            learning_history = user.get('learning_history', [])
            
            # 计算统计数据
            total_lessons = len(learning_history)
            completed_topics = len(knowledge_graph) if isinstance(knowledge_graph, dict) else 0
            
            # 计算最近学习活动
            recent_activity = []
            if learning_history:
                sorted_history = sorted(
                    learning_history, 
                    key=lambda x: x.get('completed_at', datetime.datetime.min), 
                    reverse=True
                )
                recent_activity = sorted_history[:5]  # 最近5个活动
            
            # 计算学习趋势（最近7天的学习活动）
            weekly_activity = ProgressTracker._calculate_weekly_activity(learning_history)
            
            # 计算知识点掌握情况
            topic_mastery = ProgressTracker._calculate_topic_mastery(knowledge_graph)
            
            summary = {
                'total_lessons_completed': total_lessons,
                'completed_topics': completed_topics,
                'recent_activity': recent_activity,
                'weekly_activity': weekly_activity,
                'topic_mastery': topic_mastery,
                'knowledge_level': knowledge_graph.get('level', 'beginner') if isinstance(knowledge_graph, dict) else 'beginner'
            }
            
            logger.debug(f"获取用户 {user_id} 进度摘要成功")
            return summary
        except Exception as e:
            logger.error(f"获取进度摘要失败: {e}")
            return {}
    
    @staticmethod
    def _calculate_weekly_activity(learning_history):
        """
        计算最近7天的学习活动
        
        Args:
            learning_history (list): 学习历史记录列表
            
        Returns:
            list: 每天的学习活动计数
        """
        if not learning_history:
            return [0] * 7
        
        # 获取最近7天的日期
        today = datetime.datetime.utcnow().date()
        week_dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        
        # 统计每天的活动数
        activity_count = {date: 0 for date in week_dates}
        
        for activity in learning_history:
            completed_date = activity.get('completed_at')
            if completed_date:
                date_str = completed_date.date().strftime('%Y-%m-%d')
                if date_str in activity_count:
                    activity_count[date_str] += 1
        
        # 返回按日期顺序排列的活动数
        return [activity_count[date] for date in week_dates]
    
    @staticmethod
    def _calculate_topic_mastery(knowledge_graph):
        """
        计算知识点掌握情况
        
        Args:
            knowledge_graph (dict): 知识图谱
            
        Returns:
            dict: 知识点掌握情况
        """
        if not isinstance(knowledge_graph, dict):
            return {}
        
        # 这里可以实现更复杂的掌握情况计算逻辑
        # 目前简化处理，仅返回知识点和其掌握级别
        mastery = {}
        for key, value in knowledge_graph.items():
            if key not in ['level', 'updated_at']:
                mastery[key] = value
        
        return mastery