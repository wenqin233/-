"""
用户模型
定义用户数据结构和相关操作
"""

class User:
    """用户模型类"""
    
    def __init__(self, user_id, name=None, email=None):
        """
        初始化用户对象
        
        Args:
            user_id (str): 用户唯一标识
            name (str, optional): 用户姓名
            email (str, optional): 用户邮箱
        """
        self.user_id = user_id
        self.name = name
        self.email = email
        self.knowledge_graph = {}
        self.learning_history = []
    
    def update_knowledge_graph(self, knowledge_data):
        """
        更新用户知识图谱
        
        Args:
            knowledge_data (dict): 知识图谱数据
        """
        self.knowledge_graph.update(knowledge_data)
    
    def get_knowledge_graph(self):
        """
        获取用户知识图谱
        
        Returns:
            dict: 用户知识图谱
        """
        return self.knowledge_graph
    
    def add_learning_history(self, lesson_data):
        """
        添加学习历史记录
        
        Args:
            lesson_data (dict): 课程数据
        """
        self.learning_history.append(lesson_data)
    
    def get_learning_history(self):
        """
        获取学习历史记录
        
        Returns:
            list: 学习历史记录列表
        """
        return self.learning_history
    
    def to_dict(self):
        """
        将用户对象转换为字典格式
        
        Returns:
            dict: 用户信息字典
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "knowledge_graph": self.knowledge_graph,
            "learning_history": self.learning_history
        }