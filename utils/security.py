"""
安全工具模块
用于处理密码加密、令牌生成等安全相关功能
"""

try:
    import bcrypt
    bcrypt_available = True
except ImportError:
    bcrypt = None
    bcrypt_available = False
    
import jwt
import secrets
import hashlib
import re
from datetime import datetime, timedelta
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

class SecurityUtil:
    """安全工具类"""
    
    @staticmethod
    def hash_password(password):
        """
        哈希密码
        
        Args:
            password (str): 明文密码
            
        Returns:
            str: 哈希后的密码（格式：salt:hash）
        """
        try:
            # 生成随机盐值
            salt = secrets.token_hex(16)
            # 使用SHA-256哈希密码和盐值
            hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            # 返回盐值和哈希值的组合
            return f"{salt}:{hashed}"
        except Exception as e:
            logger.error(f"密码哈希失败: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(password, hashed_password):
        """
        验证密码
        
        Args:
            password (str): 明文密码
            hashed_password (str): 哈希后的密码（格式：salt:hash）
            
        Returns:
            bool: 验证结果
        """
        try:
            # 分离盐值和哈希值
            salt, hashed = hashed_password.split(':')
            # 使用相同的盐值哈希输入密码
            rehashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            # 比较哈希值
            return hashed == rehashed
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False
    
    @staticmethod
    def generate_jwt_token(user_id, username, expires_in=7):
        """
        生成JWT令牌
        
        Args:
            user_id (str): 用户ID
            username (str): 用户名
            expires_in (int): 过期天数
            
        Returns:
            str: JWT令牌
        """
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'exp': datetime.utcnow() + timedelta(days=expires_in),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
            return token
        except Exception as e:
            logger.error(f"JWT令牌生成失败: {str(e)}")
            raise
    
    @staticmethod
    def verify_jwt_token(token):
        """
        验证JWT令牌
        
        Args:
            token (str): JWT令牌
            
        Returns:
            dict: 验证结果 {'success': bool, 'payload': dict or None}
        """
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return {'success': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return {'success': False, 'error': '令牌已过期'}
        except jwt.InvalidTokenError:
            logger.warning("JWT令牌无效")
            return {'success': False, 'error': '无效令牌'}
        except Exception as e:
            logger.error(f"JWT令牌验证失败: {str(e)}")
            return {'success': False, 'error': '令牌验证失败'}
    
    @staticmethod
    def generate_secret_key(length=32):
        """
        生成安全密钥
        
        Args:
            length (int): 密钥长度
            
        Returns:
            str: 安全密钥
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def is_strong_password(password):
        """
        检查密码强度
        
        Args:
            password (str): 密码
            
        Returns:
            dict: 检查结果 {'valid': bool, 'message': str}
        """
        if len(password) < 8:
            return {'valid': False, 'message': '密码长度至少8位'}
        
        # 移除其他密码强度要求，只检查长度
        return {'valid': True, 'message': '密码符合要求'}
    
    @staticmethod
    def sanitize_input(input_str):
        """
        清理用户输入，防止XSS攻击
        
        Args:
            input_str (str): 用户输入
            
        Returns:
            str: 清理后的字符串
        """
        if not input_str:
            return input_str
        
        # 移除潜在的危险字符
        sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
        return sanitized
    
    @staticmethod
    def rate_limit_key(ip_address, endpoint):
        """
        生成限流键值
        
        Args:
            ip_address (str): IP地址
            endpoint (str): API端点
            
        Returns:
            str: 限流键值
        """
        return f"rate_limit:{ip_address}:{endpoint}"
    
    @staticmethod
    def hash_sensitive_data(data):
        """
        哈希敏感数据用于比较，而不存储原始数据
        
        Args:
            data (str): 敏感数据
            
        Returns:
            str: 哈希值
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()