"""
数据库模块
处理MongoDB连接和基本操作
"""

from pymongo import MongoClient
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """数据库操作类"""
    
    def __init__(self):
        """初始化数据库连接"""
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client.get_default_database()
            # 测试连接
            self.client.admin.command('ping')
            logger.info("数据库连接成功")
            
            # 创建索引
            self._create_indexes()
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引以提高查询性能"""
        try:
            # 为用户集合创建索引
            users_collection = self.get_collection('users')
            users_collection.create_index('username', unique=True)
            users_collection.create_index('email', unique=True)
            users_collection.create_index('created_at')
            
            # 为学习历史创建索引
            users_collection.create_index([('learning_history.completed_at', -1)])
            
            logger.info("数据库索引创建成功")
        except Exception as e:
            logger.error(f"创建数据库索引失败: {e}")
    
    def get_collection(self, name):
        """
        获取集合对象
        
        Args:
            name (str): 集合名称
            
        Returns:
            Collection: MongoDB集合对象
        """
        return self.db[name]
    
    def insert_one(self, collection_name, document):
        """
        插入单个文档
        
        Args:
            collection_name (str): 集合名称
            document (dict): 文档数据
            
        Returns:
            InsertOneResult: 插入结果
        """
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)
    
    def find_one(self, collection_name, filter_query):
        """
        查找单个文档
        
        Args:
            collection_name (str): 集合名称
            filter_query (dict): 查询条件
            
        Returns:
            dict: 查找到的文档，未找到返回None
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(filter_query)
    
    def find_many(self, collection_name, filter_query, limit=0, skip=0, sort=None):
        """
        查找多个文档
        
        Args:
            collection_name (str): 集合名称
            filter_query (dict): 查询条件
            limit (int): 限制返回数量，0表示不限制
            skip (int): 跳过数量
            sort (list): 排序规则，例如[('created_at', -1)]
            
        Returns:
            list: 查找到的文档列表
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(filter_query)
        
        if sort:
            cursor = cursor.sort(sort)
            
        if skip > 0:
            cursor = cursor.skip(skip)
            
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def find_many_with_count(self, collection_name, filter_query, limit=0, skip=0, sort=None):
        """
        查找多个文档并返回总数（用于分页）
        
        Args:
            collection_name (str): 集合名称
            filter_query (dict): 查询条件
            limit (int): 限制返回数量，0表示不限制
            skip (int): 跳过数量
            sort (list): 排序规则
            
        Returns:
            tuple: (文档列表, 总数)
        """
        collection = self.get_collection(collection_name)
        
        # 获取总数
        total = collection.count_documents(filter_query)
        
        # 获取文档
        cursor = collection.find(filter_query)
        
        if sort:
            cursor = cursor.sort(sort)
            
        if skip > 0:
            cursor = cursor.skip(skip)
            
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor), total
    
    def update_one(self, collection_name, filter_query, update_data):
        """
        更新单个文档
        
        Args:
            collection_name (str): 集合名称
            filter_query (dict): 查询条件
            update_data (dict): 更新数据
            
        Returns:
            UpdateResult: 更新结果
        """
        collection = self.get_collection(collection_name)
        return collection.update_one(filter_query, {"$set": update_data})
    
    def delete_one(self, collection_name, filter_query):
        """
        删除单个文档
        
        Args:
            collection_name (str): 集合名称
            filter_query (dict): 查询条件
            
        Returns:
            DeleteResult: 删除结果
        """
        collection = self.get_collection(collection_name)
        return collection.delete_one(filter_query)

# 全局数据库实例
db = Database()