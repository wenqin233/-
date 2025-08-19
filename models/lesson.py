"""
课程模型
定义课程内容数据结构和相关操作
"""

class Lesson:
    """课程模型类"""
    
    def __init__(self, lesson_id, title, content=None, exercises=None):
        """
        初始化课程对象
        
        Args:
            lesson_id (str): 课程唯一标识
            title (str): 课程标题
            content (str, optional): 课程内容
            exercises (list, optional): 练习题列表
        """
        self.lesson_id = lesson_id
        self.title = title
        self.content = content or ""
        self.exercises = exercises or []
        self.created_at = None
        self.updated_at = None
    
    def set_content(self, content):
        """
        设置课程内容
        
        Args:
            content (str): 课程内容
        """
        self.content = content
    
    def add_exercise(self, exercise):
        """
        添加练习题
        
        Args:
            exercise (dict): 练习题数据
        """
        self.exercises.append(exercise)
    
    def get_content(self):
        """
        获取课程内容
        
        Returns:
            str: 课程内容
        """
        return self.content
    
    def get_exercises(self):
        """
        获取练习题列表
        
        Returns:
            list: 练习题列表
        """
        return self.exercises
    
    def to_dict(self):
        """
        将课程对象转换为字典格式
        
        Returns:
            dict: 课程信息字典
        """
        return {
            "lesson_id": self.lesson_id,
            "title": self.title,
            "content": self.content,
            "exercises": self.exercises
        }