"""
进度可视化工具
用于可视化学习进度和知识掌握情况
"""

import json
from datetime import datetime, timedelta
from database import db
from bson import ObjectId
import base64
from io import BytesIO

try:
    import matplotlib
    matplotlib.use('Agg')  # 使用非交互式后端
    import matplotlib.pyplot as plt
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    plt = None

class ProgressVisualizer:
    """进度可视化工具"""
    
    def __init__(self):
        """初始化进度可视化工具"""
        pass
    
    def generate_knowledge_map_chart(self, user_id):
        """
        生成知识掌握情况图表
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            str: 图表的base64编码数据URL
        """
        if not matplotlib_available:
            return None
            
        try:
            # 获取用户知识图谱
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            knowledge_graph = user.get('knowledge_graph', {}) if user else {}
            
            # 过滤掉非知识点数据
            topics = {k: v for k, v in knowledge_graph.items() 
                     if k not in ['level', 'updated_at'] and isinstance(v, (int, float))}
            
            if not topics:
                return None
            
            # 创建雷达图
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
            
            # 准备数据
            topic_names = list(topics.keys())
            mastery_levels = list(topics.values())
            
            # 计算角度
            angles = [n / float(len(topic_names)) * 2 * 3.14159 for n in range(len(topic_names))]
            angles += angles[:1]  # 闭合图形
            
            # 添加数据
            mastery_levels += mastery_levels[:1]  # 闭合图形
            
            # 绘制
            ax.plot(angles, mastery_levels, 'o-', linewidth=2, color='#4361ee')
            ax.fill(angles, mastery_levels, alpha=0.25, color='#4361ee')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(topic_names)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_yticklabels(['25%', '50%', '75%', '100%'])
            ax.set_title('知识点掌握情况', pad=20)
            
            # 保存为base64
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"生成知识掌握情况图表时出错: {e}")
            return None
    
    def generate_progress_timeline_chart(self, user_id, days=30):
        """
        生成学习进度时间线图表
        
        Args:
            user_id (str): 用户ID
            days (int): 天数范围
            
        Returns:
            str: 图表的base64编码数据URL
        """
        if not matplotlib_available:
            return None
            
        try:
            # 获取用户学习历史
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            learning_history = user.get('learning_history', []) if user else []
            
            # 计算日期范围
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 按日期统计学习活动
            daily_activity = {}
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                daily_activity[date_str] = 0
                current_date += timedelta(days=1)
            
            # 统计学习历史
            for activity in learning_history:
                completed_at = activity.get('completed_at')
                if completed_at and isinstance(completed_at, datetime):
                    date_str = completed_at.strftime('%Y-%m-%d')
                    if date_str in daily_activity:
                        daily_activity[date_str] += 1
            
            # 创建折线图
            fig, ax = plt.subplots(figsize=(10, 6))
            
            dates = list(daily_activity.keys())
            activities = list(daily_activity.values())
            
            ax.plot(dates, activities, marker='o', linewidth=2, markersize=4, color='#4361ee')
            ax.fill_between(dates, activities, alpha=0.25, color='#4361ee')
            ax.set_xlabel('日期')
            ax.set_ylabel('学习活动数')
            ax.set_title(f'最近{days}天学习活动统计')
            ax.grid(True, alpha=0.3)
            
            # 设置x轴标签间隔以避免重叠
            if len(dates) > 10:
                step = len(dates) // 10
                ax.set_xticks(dates[::step])
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存为base64
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"生成学习进度时间线图表时出错: {e}")
            return None
    
    def generate_topic_mastery_chart(self, user_id):
        """
        生成主题掌握情况柱状图
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            str: 图表的base64编码数据URL
        """
        if not matplotlib_available:
            return None
            
        try:
            # 获取用户知识图谱
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            knowledge_graph = user.get('knowledge_graph', {}) if user else {}
            
            # 过滤知识点数据
            topics = {k: v for k, v in knowledge_graph.items() 
                     if k not in ['level', 'updated_at'] and isinstance(v, (int, float))}
            
            if not topics:
                return None
            
            # 创建柱状图
            fig, ax = plt.subplots(figsize=(10, 6))
            
            topic_names = list(topics.keys())
            mastery_levels = list(topics.values())
            
            bars = ax.bar(range(len(topic_names)), mastery_levels, 
                         color=['#4361ee' if x < 0.5 else '#4cc9f0' if x < 0.8 else '#4caf50' 
                               for x in mastery_levels])
            
            ax.set_xlabel('知识点')
            ax.set_ylabel('掌握程度')
            ax.set_title('各知识点掌握情况')
            ax.set_xticks(range(len(topic_names)))
            ax.set_xticklabels(topic_names, rotation=45, ha='right')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for i, (bar, level) in enumerate(zip(bars, mastery_levels)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{level:.2f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # 保存为base64
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.read()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"生成主题掌握情况图表时出错: {e}")
            return None
    
    def get_progress_summary(self, user_id):
        """
        获取进度摘要数据
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 进度摘要数据
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            if not user:
                return {}
            
            knowledge_graph = user.get('knowledge_graph', {})
            learning_history = user.get('learning_history', [])
            
            # 计算统计数据
            total_lessons = len(learning_history)
            completed_topics = len([k for k in knowledge_graph.keys() 
                                  if k not in ['level', 'updated_at']])
            
            # 计算平均掌握程度
            mastery_values = [v for k, v in knowledge_graph.items() 
                            if k not in ['level', 'updated_at'] and isinstance(v, (int, float))]
            avg_mastery = sum(mastery_values) / len(mastery_values) if mastery_values else 0
            
            # 计算学习趋势（最近7天的学习活动）
            weekly_activity = self._calculate_weekly_activity(learning_history)
            
            # 知识水平
            knowledge_level = knowledge_graph.get('level', 'beginner')
            
            # 最近学习活动
            recent_activity = []
            if learning_history:
                sorted_history = sorted(
                    learning_history, 
                    key=lambda x: x.get('completed_at', datetime.min), 
                    reverse=True
                )
                recent_activity = sorted_history[:5]  # 最近5个活动
            
            summary = {
                'total_lessons_completed': total_lessons,
                'completed_topics': completed_topics,
                'average_mastery': round(avg_mastery, 2),
                'weekly_activity': weekly_activity,
                'knowledge_level': knowledge_level,
                'recent_activity': recent_activity,
                'last_updated': knowledge_graph.get('updated_at', datetime.utcnow())
            }
            
            return summary
            
        except Exception as e:
            print(f"获取进度摘要时出错: {e}")
            return {}
    
    def _calculate_weekly_activity(self, learning_history):
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
        today = datetime.utcnow().date()
        week_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        
        # 统计每天的活动数
        activity_count = {date: 0 for date in week_dates}
        
        for activity in learning_history:
            completed_date = activity.get('completed_at')
            if completed_date and isinstance(completed_date, datetime):
                date_str = completed_date.date().strftime('%Y-%m-%d')
                if date_str in activity_count:
                    activity_count[date_str] += 1
        
        # 返回按日期顺序排列的活动数
        return [activity_count[date] for date in week_dates]
    
    def generate_learning_report(self, user_id):
        """
        生成学习报告
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            dict: 学习报告数据
        """
        # 获取进度摘要
        summary = self.get_progress_summary(user_id)
        
        # 生成图表
        knowledge_map_chart = self.generate_knowledge_map_chart(user_id)
        progress_timeline_chart = self.generate_progress_timeline_chart(user_id)
        topic_mastery_chart = self.generate_topic_mastery_chart(user_id)
        
        report = {
            'summary': summary,
            'charts': {
                'knowledge_map': knowledge_map_chart,
                'progress_timeline': progress_timeline_chart,
                'topic_mastery': topic_mastery_chart
            },
            'generated_at': datetime.utcnow()
        }
        
        return report
    
    def get_topic_progress(self, user_id, topic):
        """
        获取特定主题的学习进度
        
        Args:
            user_id (str): 用户ID
            topic (str): 主题名称
            
        Returns:
            dict: 主题学习进度
        """
        try:
            user = db.find_one('users', {'_id': ObjectId(user_id)})
            if not user:
                return {}
            
            knowledge_graph = user.get('knowledge_graph', {})
            learning_history = user.get('learning_history', [])
            
            # 获取主题掌握程度
            mastery = knowledge_graph.get(topic, 0)
            
            # 统计该主题的学习活动
            topic_activities = [activity for activity in learning_history 
                              if activity.get('topic') == topic]
            
            # 计算相关统计数据
            time_spent = sum(activity.get('time_spent', 0) for activity in topic_activities)
            exercises_completed = len([activity for activity in topic_activities 
                                     if activity.get('type') == 'exercise'])
            
            # 计算练习正确率
            correct_exercises = len([activity for activity in topic_activities 
                                   if activity.get('type') == 'exercise' and activity.get('correct', False)])
            accuracy = correct_exercises / exercises_completed if exercises_completed > 0 else 0
            
            return {
                'topic': topic,
                'mastery': mastery,
                'time_spent': time_spent,
                'exercises_completed': exercises_completed,
                'accuracy': round(accuracy, 2),
                'activities': topic_activities[-10:]  # 最近10个活动
            }
            
        except Exception as e:
            print(f"获取主题进度时出错: {e}")
            return {}