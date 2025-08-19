"""
日志配置模块
配置应用的日志记录功能
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """
    设置应用日志配置
    
    Args:
        app (Flask): Flask应用实例
    """
    # 确保日志目录存在
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 配置文件处理器
    file_handler = RotatingFileHandler(
        'logs/ai_learning_companion.log', 
        maxBytes=10240, 
        backupCount=10
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    # 设置日志级别
    file_handler.setLevel(logging.INFO)
    
    # 添加处理器到应用
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # 记录应用启动日志
    app.logger.info('AI个性化学习伴侣启动')

def get_logger(name):
    """
    获取指定名称的日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果记录器已经有处理器，则直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger