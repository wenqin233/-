#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境配置脚本
帮助用户设置API密钥和其他环境变量
"""

import os

def setup_env():
    """设置环境变量"""
    print("=" * 50)
    print("🔧 AI个性化学习伴侣 - 环境配置工具")
    print("=" * 50)
    
    # 检查是否存在.env文件
    env_file = '.env'
    if os.path.exists(env_file):
        print("📝 检测到现有的 .env 文件")
        choice = input("是否要重新配置？(y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("✅ 使用现有配置")
            return
    
    print("\n请提供以下信息来配置环境变量:")
    print("-" * 50)
    
    # 收集用户输入
    dashscope_key = input("阿里云百炼 API 密钥 (可选，直接回车跳过): ").strip()
    
    # 如果用户没有输入任何密钥，给出提示
    if not dashscope_key:
        print("\n⚠️  未输入API密钥，系统将使用预定义内容")
        print("💡 建议配置API密钥以启用个性化内容生成")
    
    # 生成.env文件内容
    env_content = f"""# 环境变量配置文件
# AI个性化学习伴侣

# Flask配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 阿里云百炼API配置
"""

    if dashscope_key:
        env_content += f"DASHSCOPE_API_KEY={dashscope_key}\n"
    else:
        env_content += "# DASHSCOPE_API_KEY=your-dashscope-api-key-here\n"
    
    env_content += """

# 数据库配置
MONGO_URI=mongodb://localhost:27017/ai_learning_companion

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis配置（用于Celery）
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
    
    # 写入.env文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"\n✅ 环境配置已保存到 {env_file}")
        
        # 显示配置摘要
        print("\n📋 配置摘要:")
        print(f"  阿里云百炼 API: {'✅ 已配置' if dashscope_key else '❌ 未配置'}")
        print(f"  OpenAI API: {'✅ 已配置' if openai_key else '❌ 未配置'}")
        
    except Exception as e:
        print(f"\n❌ 保存配置文件时出错: {e}")
        print("请手动创建 .env 文件并添加配置")

def show_instructions():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("📖 使用说明")
    print("=" * 50)
    print("1. 运行此脚本配置API密钥:")
    print("   python setup_env.py")
    print()
    print("2. 启动应用:")
    print("   python app.py")
    print()
    print("3. 测试API集成:")
    print("   python test_llm_api.py")
    print()
    print("💡 提示:")
    print("   - 您可以随时手动编辑 .env 文件来修改配置")
    print("   - 配置API密钥以获得最佳体验")
    print("   - API密钥可以从阿里云百炼平台的开发者控制台获取")

if __name__ == "__main__":
    setup_env()
    show_instructions()