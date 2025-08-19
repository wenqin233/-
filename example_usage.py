#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用示例脚本
展示如何使用集成的阿里云百炼API生成个性化学习内容
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.content_generator import ContentGenerator
from utils.knowledge_analyzer import KnowledgeAnalyzer

def demo_personalized_content_generation():
    """演示个性化内容生成"""
    print("=" * 60)
    print("🎓 AI个性化学习伴侣 - 内容生成演示")
    print("=" * 60)
    
    # 创建内容生成器实例
    content_generator = ContentGenerator()
    knowledge_analyzer = KnowledgeAnalyzer()
    
    print(f"🔍 当前使用的API类型: {content_generator.api_type or '预定义内容'}")
    print()
    
    # 模拟用户知识水平分析结果
    print("📊 用户知识水平分析...")
    user_knowledge_graph = {
        "python_basics": 0.3,  # 30%掌握
        "data_structures": 0.1,  # 10%掌握
        "web_development": 0.0   # 未掌握
    }
    
    # 分析用户水平
    level_analysis = knowledge_analyzer.analyze_user_level(user_knowledge_graph)
    print(f"  用户水平: {level_analysis['level']}")
    print(f"  掌握程度: {level_analysis['confidence']:.2f}")
    print()
    
    # 选择学习主题
    learning_goal = "python_basics"
    print(f"🎯 学习目标: {learning_goal}")
    
    # 检索学习材料
    materials = content_generator.retrieve_materials(learning_goal, level_analysis)
    print(f"📚 学习主题: {materials.get('concept', '未知')}")
    print(f"📋 关键知识点: {', '.join(materials.get('key_points', []))}")
    print()
    
    # 生成解释内容
    print("📖 生成个性化解释内容...")
    explanation = content_generator.generate_explanation(
        level_analysis, 
        materials, 
        user_knowledge_graph
    )
    print("-" * 40)
    print(explanation)
    print("-" * 40)
    print()
    
    # 生成练习题
    print("✏️ 生成个性化练习题...")
    exercises = content_generator.generate_exercises(
        level_analysis, 
        materials
    )
    print(f"  共生成 {len(exercises)} 道练习题:")
    print()
    
    for i, exercise in enumerate(exercises, 1):
        print(f"  题目 {i}: {exercise['type']}")
        print(f"  问题: {exercise['question']}")
        if exercise['type'] == 'multiple_choice':
            print("  选项:")
            for j, option in enumerate(exercise['options'], 1):
                print(f"    {chr(64+j)}. {option}")
            print(f"  答案: {exercise['answer']}")
        else:
            print(f"  答案: {exercise['answer']}")
        print()

def show_available_topics():
    """显示可用的学习主题"""
    print("📚 可用学习主题:")
    print("-" * 30)
    
    content_generator = ContentGenerator()
    topics = content_generator.get_available_topics()
    
    for topic in topics:
        info = content_generator.get_topic_info(topic)
        if info:
            print(f"  {topic}: {info['concept']}")
            print(f"    关键知识点: {', '.join(info['key_points'])}")
            print()

def main():
    """主函数"""
    print("🚀 欢迎使用AI个性化学习伴侣!")
    print()
    
    # 显示可用主题
    show_available_topics()
    
    # 演示个性化内容生成
    demo_personalized_content_generation()
    
    print("=" * 60)
    print("✨ 演示完成!")
    print()
    print("💡 提示:")
    print("   - 系统会根据用户的知识水平自动调整内容难度")
    print("   - 练习题会根据用户掌握的知识点进行个性化生成")
    print("   - 您可以随时更换学习主题")
    print("=" * 60)

if __name__ == "__main__":
    main()