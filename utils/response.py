"""
统一响应格式模块
用于生成标准化的API响应
"""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class ResponseUtil:
    """响应工具类"""
    
    @staticmethod
    def success(data=None, message="操作成功", status_code=200):
        """
        生成成功响应
        
        Args:
            data (any): 响应数据
            message (str): 响应消息
            status_code (int): HTTP状态码
            
        Returns:
            tuple: (Response, status_code)
        """
        response = {
            'success': True,
            'message': message
        }
        
        if data is not None:
            response['data'] = data
            
        logger.debug(f"成功响应: {message}")
        return jsonify(response), status_code
    
    @staticmethod
    def error(message="操作失败", status_code=400, data=None):
        """
        生成错误响应
        
        Args:
            message (str): 错误消息
            status_code (int): HTTP状态码
            data (any): 额外数据
            
        Returns:
            tuple: (Response, status_code)
        """
        response = {
            'success': False,
            'error': message
        }
        
        if data is not None:
            response['data'] = data
            
        logger.warning(f"错误响应: {message}")
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(data, page, per_page, total, message="获取成功"):
        """
        生成分页响应
        
        Args:
            data (list): 数据列表
            page (int): 当前页码
            per_page (int): 每页数量
            total (int): 总数量
            message (str): 响应消息
            
        Returns:
            tuple: (Response, status_code)
        """
        response = {
            'success': True,
            'message': message,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page  # 向上取整计算总页数
            }
        }
        
        logger.debug(f"分页响应: 第{page}页，共{total}条记录")
        return jsonify(response), 200