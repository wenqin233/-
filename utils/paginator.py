"""
分页处理模块
用于处理数据库查询结果的分页
"""

from flask import request
import math

class Paginator:
    """分页器类"""
    
    def __init__(self, page=None, per_page=None, max_per_page=100):
        """
        初始化分页器
        
        Args:
            page (int): 页码
            per_page (int): 每页数量
            max_per_page (int): 每页最大数量
        """
        self.page = page or self._get_page_from_request()
        self.per_page = per_page or self._get_per_page_from_request()
        self.max_per_page = max_per_page
        
        # 限制每页数量不超过最大值
        if self.per_page > self.max_per_page:
            self.per_page = self.max_per_page
        
        # 确保页码和每页数量为正整数
        self.page = max(1, self.page)
        self.per_page = max(1, self.per_page)
    
    def _get_page_from_request(self):
        """从请求中获取页码"""
        try:
            return int(request.args.get('page', 1))
        except (TypeError, ValueError):
            return 1
    
    def _get_per_page_from_request(self):
        """从请求中获取每页数量"""
        try:
            return int(request.args.get('per_page', 10))
        except (TypeError, ValueError):
            return 10
    
    def paginate_list(self, items):
        """
        对列表进行分页
        
        Args:
            items (list): 要分页的列表
            
        Returns:
            tuple: (分页数据, 总数)
        """
        total = len(items)
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        paginated_items = items[start:end]
        
        return paginated_items, total
    
    def get_offset(self):
        """
        获取数据库查询偏移量
        
        Returns:
            int: 偏移量
        """
        return (self.page - 1) * self.per_page
    
    def get_pagination_info(self, total):
        """
        获取分页信息
        
        Args:
            total (int): 总记录数
            
        Returns:
            dict: 分页信息
        """
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total': total,
            'pages': math.ceil(total / self.per_page)
        }
    
    @staticmethod
    def get_default_pagination():
        """
        获取默认分页参数
        
        Returns:
            tuple: (page, per_page)
        """
        return 1, 10