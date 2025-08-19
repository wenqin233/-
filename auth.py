"""
认证模块
处理用户认证
"""

from database import db
from utils.security import SecurityUtil
import logging
from datetime import datetime
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

# 简单的内存登录尝试记录（在生产环境中应使用Redis等）
login_attempts = defaultdict(list)

class Auth:
    """认证类"""
    
    @staticmethod
    def register_user(username, email, password):
        """
        注册新用户
        
        Args:
            username (str): 用户名
            email (str): 邮箱
            password (str): 密码
            
        Returns:
            dict: 注册结果和用户信息
        """
        try:
            # 检查密码强度
            password_check = SecurityUtil.is_strong_password(password)
            if not password_check['valid']:
                return {'success': False, 'message': password_check['message']}
            
            # 检查用户是否已存在
            existing_user = db.find_one('users', {'$or': [{'username': username}, {'email': email}]})
            if existing_user:
                return {'success': False, 'message': '用户名或邮箱已存在'}
            
            # 密码加密
            hashed_password = SecurityUtil.hash_password(password)
            
            # 创建用户文档
            user_doc = {
                'username': username,
                'email': email,
                'password': hashed_password,
                'created_at': datetime.utcnow(),
                'knowledge_graph': {},
                'learning_history': []
            }
            
            # 插入数据库
            result = db.insert_one('users', user_doc)
            
            if result.inserted_id:
                logger.info(f"用户注册成功: {username}")
                return {
                    'success': True, 
                    'message': '注册成功',
                    'user_id': str(result.inserted_id),
                    'username': username
                }
            else:
                logger.error("用户注册失败: 数据库插入失败")
                return {'success': False, 'message': '注册失败'}
                
        except Exception as e:
            logger.error(f"用户注册过程中出错: {str(e)}")
            return {'success': False, 'message': '注册失败'}
    
    @staticmethod
    def authenticate_user(username, password, ip_address=None):
        """
        验证用户登录
        
        Args:
            username (str): 用户名或邮箱
            password (str): 密码
            ip_address (str): IP地址（用于限流）
            
        Returns:
            dict: 认证结果和令牌信息
        """
        # 检查登录尝试次数
        if ip_address and Auth._is_rate_limited(ip_address):
            logger.warning(f"IP地址 {ip_address} 登录尝试过于频繁")
            return {'success': False, 'message': '登录尝试过于频繁，请稍后再试'}
            
        try:
            # 查找用户
            user = db.find_one('users', {'$or': [{'username': username}, {'email': username}]})
            if not user:
                logger.warning(f"用户登录失败: 用户不存在 ({username})")
                # 记录失败的登录尝试
                if ip_address:
                    Auth._record_failed_attempt(ip_address)
                return {'success': False, 'message': '用户不存在'}
            
            # 验证密码
            if SecurityUtil.verify_password(password, user['password']):
                # 生成JWT令牌
                token = SecurityUtil.generate_jwt_token(
                    str(user['_id']), 
                    user['username']
                )
                
                # 清除之前的失败尝试记录
                if ip_address:
                    Auth._clear_failed_attempts(ip_address)
                
                logger.info(f"用户登录成功: {username}")
                return {
                    'success': True,
                    'message': '登录成功',
                    'token': token,
                    'user_id': str(user['_id']),
                    'username': user['username']
                }
            else:
                logger.warning(f"用户登录失败: 密码错误 ({username})")
                # 记录失败的登录尝试
                if ip_address:
                    Auth._record_failed_attempt(ip_address)
                return {'success': False, 'message': '密码错误'}
                
        except Exception as e:
            logger.error(f"用户登录过程中出错: {str(e)}")
            return {'success': False, 'message': '登录失败'}
    
    
    @staticmethod
    def _record_failed_attempt(ip_address):
        """
        记录失败的登录尝试
        
        Args:
            ip_address (str): IP地址
        """
        current_time = time.time()
        login_attempts[ip_address].append(current_time)
        
        # 只保留最近10分钟的尝试记录
        cutoff_time = current_time - 600  # 10分钟
        login_attempts[ip_address] = [
            timestamp for timestamp in login_attempts[ip_address] 
            if timestamp > cutoff_time
        ]
    
    @staticmethod
    def _clear_failed_attempts(ip_address):
        """
        清除IP地址的失败登录尝试记录
        
        Args:
            ip_address (str): IP地址
        """
        if ip_address in login_attempts:
            del login_attempts[ip_address]
    
    @staticmethod
    def _is_rate_limited(ip_address):
        """
        检查IP地址是否被限流
        
        Args:
            ip_address (str): IP地址
            
        Returns:
            bool: 是否被限流
        """
        if ip_address not in login_attempts:
            return False
        
        current_time = time.time()
        # 只考虑最近5分钟的尝试
        cutoff_time = current_time - 300  # 5分钟
        recent_attempts = [
            timestamp for timestamp in login_attempts[ip_address] 
            if timestamp > cutoff_time
        ]
        
        # 如果最近5分钟内尝试超过5次，则限流
        return len(recent_attempts) >= 5