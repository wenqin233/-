#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试大语言模型API集成
用于验证阿里云百炼API是否正常工作
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

def test_dashscope_api():
    """测试阿里云百炼API"""
    try:
        from dashscope import Generation
        import dashscope
        
        # 获取API密钥
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            print("❌ 未找到DASHSCOPE_API_KEY环境变量")
            return False
            
        # 设置API密钥
        dashscope.api_key = api_key
        
        print("🔄 正在测试阿里云百炼API...")
        
        # 测试API调用
        response = Generation.call(
            model='qwen-plus',
            prompt='请用中文简要介绍Python编程语言，100字以内',
            max_tokens=500,
            temperature=0.7
        )
        
        if response.status_code == 200:
            print("✅ 阿里云百炼API调用成功！")
            print(f"📝 生成内容: {response.output.text}")
            return True
        else:
            print(f"❌ 阿里云百炼API调用失败: {response}")
            return False
            
    except ImportError:
        print("❌ 未安装dashscope库，请运行: pip install dashscope")
        return False
    except Exception as e:
        print(f"❌ 阿里云百炼API测试出错: {e}")
        return False


def test_content_generator():
    """测试内容生成器"""
    try:
        print("🔄 正在测试内容生成器...")
        
        # 导入内容生成器
        from utils.content_generator import ContentGenerator
        
        # 创建内容生成器实例
        generator = ContentGenerator()
        
        # 检查API类型
        print(f"🔍 当前使用的API类型: {generator.api_type or '预定义内容'}")
        
        # 测试材料检索
        materials = generator.retrieve_materials("python_basics", {"level": "beginner"})
        print(f"📚 检索到学习材料: {materials['concept'] if materials else '无'}")
        
        # 测试解释内容生成
        explanation = generator.generate_explanation(
            {"level": "beginner"}, 
            materials, 
            {"python_basics": 0.3}
        )
        print(f"📝 生成的解释内容预览: {explanation[:100]}...")
        
        # 测试练习题生成
        exercises = generator.generate_exercises(
            {"level": "beginner"}, 
            materials
        )
        print(f"✏️ 生成的练习题数量: {len(exercises)}")
        
        print("✅ 内容生成器测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 内容生成器测试出错: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("🔍 环境配置检查")
    print("-" * 30)
    
    # 检查环境变量文件
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("✅ .env 文件存在")
        # 读取并显示关键环境变量的状态
        dashscope_key = "✅ 已设置" if os.getenv('DASHSCOPE_API_KEY') else "❌ 未设置"
        
        print(f"🔑 DASHSCOPE_API_KEY: {dashscope_key}")
    else:
        print("⚠️  .env 文件不存在，请复制 .env.example 并配置相关参数")
        
    print()

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 大语言模型API集成测试")
    print("=" * 50)
    
    # 检查环境配置
    check_environment()
    
    # 测试各个组件
    tests = [
        ("阿里云百炼API", test_dashscope_api),
        ("内容生成器", test_content_generator)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！大语言模型API集成正常工作。")
        print("💡 您现在可以使用系统生成个性化的学习内容了。")
    else:
        print("⚠️  部分测试失败，请检查相关配置和依赖。")
        print("💡 请确保已在 .env 文件中正确配置 API 密钥。")
    print("=" * 50)

if __name__ == "__main__":
    main()