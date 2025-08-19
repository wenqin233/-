"""
输入验证模块
用于验证API请求参数，确保数据安全性和一致性
"""

import re
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """自定义验证异常"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class Validator:
    """输入验证器"""
    
    @staticmethod
    def required(field_name, value):
        """验证字段是否必需"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} 是必需的", field_name)
        return value
    
    @staticmethod
    def string(field_name, value, min_length=0, max_length=None):
        """验证字符串字段"""
        if value is None:
            return value
            
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} 必须是字符串", field_name)
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} 长度不能少于 {min_length} 个字符", field_name)
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} 长度不能超过 {max_length} 个字符", field_name)
        
        return value
    
    @staticmethod
    def email(field_name, value):
        """验证邮箱格式"""
        value = Validator.string(field_name, value)
        if value is None:
            return value
            
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise ValidationError(f"{field_name} 邮箱格式不正确", field_name)
        
        return value
    
    @staticmethod
    def integer(field_name, value, min_value=None, max_value=None):
        """验证整数字段"""
        if value is None:
            return value
            
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} 必须是整数", field_name)
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} 不能小于 {min_value}", field_name)
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} 不能大于 {max_value}", field_name)
        
        return value
    
    @staticmethod
    def boolean(field_name, value):
        """验证布尔字段"""
        if value is None:
            return value
            
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        raise ValidationError(f"{field_name} 必须是布尔值", field_name)

def validate_request(schema):
    """
    装饰器：验证请求参数
    
    Args:
        schema (dict): 验证规则字典
            格式: {
                'field_name': {
                    'required': bool,
                    'type': 'string'|'email'|'integer'|'boolean',
                    'min_length': int,
                    'max_length': int,
                    'min_value': int,
                    'max_value': int
                }
            }
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() or request.form.to_dict() or {}
            
            validated_data = {}
            
            try:
                for field_name, rules in schema.items():
                    value = data.get(field_name)
                    
                    # 检查必需字段
                    if rules.get('required', False):
                        Validator.required(field_name, value)
                    
                    # 如果字段为空且非必需，跳过其他验证
                    if value is None and not rules.get('required', False):
                        validated_data[field_name] = value
                        continue
                    
                    # 根据类型进行验证
                    field_type = rules.get('type', 'string')
                    
                    if field_type == 'string':
                        validated_data[field_name] = Validator.string(
                            field_name, 
                            value, 
                            rules.get('min_length', 0), 
                            rules.get('max_length')
                        )
                    elif field_type == 'email':
                        validated_data[field_name] = Validator.email(field_name, value)
                    elif field_type == 'integer':
                        validated_data[field_name] = Validator.integer(
                            field_name, 
                            value, 
                            rules.get('min_value'), 
                            rules.get('max_value')
                        )
                    elif field_type == 'boolean':
                        validated_data[field_name] = Validator.boolean(field_name, value)
                    else:
                        validated_data[field_name] = value
                
                # 将验证后的数据添加到请求上下文
                request.validated_data = validated_data
                
            except ValidationError as e:
                logger.warning(f"参数验证失败: {e.message}")
                return jsonify({
                    'success': False,
                    'error': e.message,
                    'field': e.field
                }), 400
            except Exception as e:
                logger.error(f"参数验证过程中出错: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': '参数验证失败'
                }), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator