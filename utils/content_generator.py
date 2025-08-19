"""
内容生成器工具模块
用于生成个性化的学习内容和练习题
支持使用阿里云百炼API生成真实自适应内容
"""

import random
import json
import logging
from config import Config

try:
    from dashscope import Generation
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    dashscope = None
    Generation = None

logger = logging.getLogger(__name__)

class ContentGenerator:
    """内容生成器"""
    
    def __init__(self):
        """初始化内容生成器"""
        # 初始化API
        self._init_llm_api()
        
        # 学习材料库（当API不可用时的回退选项）
        self.learning_materials = {
            "python_basics": {
                "concept": "Python基础",
                "key_points": ["变量", "数据类型", "控制结构"],
                "content": {
                    "beginner": "Python是一种易于学习的编程语言。它以简洁的语法和强大的功能而闻名。对于初学者来说，Python是一个很好的起点。在Python中，你不需要声明变量的类型，这使得代码更简洁易读。",
                    "intermediate": "Python的高级特性包括生成器、装饰器、上下文管理器等。这些特性可以帮助你编写更高效和优雅的代码。例如，生成器可以节省内存，装饰器可以增强函数功能。",
                    "advanced": "Python的内存管理和性能优化涉及理解垃圾回收机制、使用性能分析工具、以及采用适当的数据结构。对于高性能需求，可以考虑使用Cython或集成C/C++代码。"
                },
                "exercises": {
                    "beginner": [
                        {
                            "type": "multiple_choice",
                            "question": "以下哪个是Python的合法变量名？",
                            "options": ["1variable", "variable-1", "variable_1", "variable 1"],
                            "answer": "variable_1"
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Python中哪个关键字用于定义函数？",
                            "options": ["func", "function", "def", "define"],
                            "answer": "def"
                        }
                    ],
                    "intermediate": [
                        {
                            "type": "coding",
                            "question": "编写一个装饰器，用于计算函数执行时间",
                            "answer": "示例实现使用time模块和装饰器语法"
                        },
                        {
                            "type": "multiple_choice",
                            "question": "以下哪个不是Python的数据结构？",
                            "options": ["list", "tuple", "dict", "map"],
                            "answer": "map"
                        }
                    ],
                    "advanced": [
                        {
                            "type": "conceptual",
                            "question": "解释Python的GIL（全局解释器锁）及其对多线程性能的影响",
                            "answer": "GIL确保同一时刻只有一个线程执行Python字节码"
                        },
                        {
                            "type": "coding",
                            "question": "如何使用生成器优化内存使用？请给出示例",
                            "answer": "使用yield关键字创建生成器函数"
                        }
                    ]
                }
            },
            "machine_learning": {
                "concept": "机器学习基础",
                "key_points": ["监督学习", "无监督学习", "模型评估"],
                "content": {
                    "beginner": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出预测或决策，而无需明确编程。监督学习使用标记数据进行训练，无监督学习则处理未标记数据。",
                    "intermediate": "常见的机器学习算法包括线性回归、决策树、支持向量机和神经网络。特征工程和模型选择对性能有很大影响。交叉验证是评估模型性能的重要技术。",
                    "advanced": "深度学习使用多层神经网络处理复杂模式。集成方法结合多个模型以提高性能。超参数优化和正则化技术防止过拟合。"
                },
                "exercises": {
                    "beginner": [
                        {
                            "type": "multiple_choice",
                            "question": "以下哪种算法属于无监督学习？",
                            "options": ["线性回归", "K-means聚类", "决策树", "支持向量机"],
                            "answer": "K-means聚类"
                        },
                        {
                            "type": "multiple_choice",
                            "question": "什么是过拟合？",
                            "options": [
                                "模型在训练数据上表现差但在测试数据上表现好",
                                "模型在训练数据和测试数据上都表现差",
                                "模型在训练数据上表现好但在测试数据上表现差",
                                "模型在训练数据和测试数据上都表现好"
                            ],
                            "answer": "模型在训练数据上表现好但在测试数据上表现差"
                        }
                    ],
                    "intermediate": [
                        {
                            "type": "coding",
                            "question": "使用scikit-learn实现一个简单的分类器并评估其性能",
                            "answer": "使用train_test_split分割数据，用准确率和混淆矩阵评估"
                        },
                        {
                            "type": "conceptual",
                            "question": "解释交叉验证的作用",
                            "answer": "交叉验证用于更可靠地评估模型性能"
                        }
                    ],
                    "advanced": [
                        {
                            "type": "conceptual",
                            "question": "比较随机森林和梯度提升机的优缺点",
                            "answer": "随机森林并行训练，抗过拟合能力强；梯度提升机序列训练，通常精度更高"
                        },
                        {
                            "type": "coding",
                            "question": "实现一个简单的神经网络模型",
                            "answer": "使用TensorFlow或PyTorch构建网络"
                        }
                    ]
                }
            },
            "web_development": {
                "concept": "Web开发基础",
                "key_points": ["HTML基础", "CSS样式", "JavaScript交互"],
                "content": {
                    "beginner": "Web开发是创建网站和Web应用程序的过程。它主要包括前端开发（用户界面）和后端开发（服务器逻辑）。HTML用于构建网页结构，CSS用于样式设计，JavaScript用于交互功能。",
                    "intermediate": "响应式设计确保网站在不同设备上都能良好显示。前端框架如React、Vue.js可以提高开发效率。后端技术如Node.js、Python Flask可以处理服务器逻辑。",
                    "advanced": "现代Web开发涉及构建工具（Webpack、Vite）、状态管理（Redux、Vuex）、服务端渲染（SSR）、静态站点生成（SSG）等高级概念。安全性、性能优化和可访问性也是重要考虑因素。"
                },
                "exercises": {
                    "beginner": [
                        {
                            "type": "multiple_choice",
                            "question": "以下哪个标签用于定义HTML文档的标题？",
                            "options": ["<header>", "<title>", "<head>", "<h1>"],
                            "answer": "<title>"
                        },
                        {
                            "type": "coding",
                            "question": "编写一个简单的HTML页面，包含标题、段落和链接",
                            "answer": "使用<h1>、<p>、<a>标签"
                        }
                    ],
                    "intermediate": [
                        {
                            "type": "coding",
                            "question": "使用CSS创建一个居中显示的卡片组件",
                            "answer": "使用Flexbox或Grid布局"
                        },
                        {
                            "type": "multiple_choice",
                            "question": "JavaScript中哪个方法用于选择HTML元素？",
                            "options": [
                                "getElementById()",
                                "querySelector()",
                                "getElementsByClassName()",
                                "以上都是"
                            ],
                            "answer": "以上都是"
                        }
                    ],
                    "advanced": [
                        {
                            "type": "conceptual",
                            "question": "解释RESTful API设计原则",
                            "answer": "使用HTTP方法表示操作，URL表示资源等"
                        },
                        {
                            "type": "coding",
                            "question": "实现一个简单的React组件，包含状态管理和事件处理",
                            "answer": "使用useState钩子和事件处理器"
                        }
                    ]
                }
            },
            "data_structures": {
                "concept": "数据结构与算法",
                "key_points": ["数组", "链表", "树", "图"],
                "content": {
                    "beginner": "数据结构是组织和存储数据的方式，算法是解决问题的步骤。常见的数据结构包括数组、栈、队列、链表等。理解这些基础知识对编程非常重要。",
                    "intermediate": "树和图是更复杂的数据结构。二叉树、平衡树、堆等在实际应用中非常有用。排序和搜索算法如快速排序、二分查找是必须掌握的算法。",
                    "advanced": "高级数据结构包括哈希表、并查集、线段树、字典树等。图算法如最短路径、最小生成树在解决复杂问题时非常有用。动态规划和贪心算法是重要的算法设计思想。"
                },
                "exercises": {
                    "beginner": [
                        {
                            "type": "multiple_choice",
                            "question": "以下哪个数据结构遵循后进先出（LIFO）原则？",
                            "options": ["队列", "栈", "数组", "链表"],
                            "answer": "栈"
                        },
                        {
                            "type": "coding",
                            "question": "实现一个栈的数据结构，包含push和pop方法",
                            "answer": "使用列表或链表实现"
                        }
                    ],
                    "intermediate": [
                        {
                            "type": "coding",
                            "question": "实现二分查找算法",
                            "answer": "在有序数组中查找元素"
                        },
                        {
                            "type": "conceptual",
                            "question": "解释哈希表的工作原理",
                            "answer": "通过哈希函数将键映射到数组索引"
                        }
                    ],
                    "advanced": [
                        {
                            "type": "coding",
                            "question": "实现快速排序算法",
                            "answer": "采用分治思想进行排序"
                        },
                        {
                            "type": "conceptual",
                            "question": "解释动态规划的基本思想",
                            "answer": "将复杂问题分解为子问题并存储子问题的解"
                        }
                    ]
                }
            }
        }
    
    def _init_llm_api(self):
        """初始化阿里云百炼API"""
        self.api_type = None
        self.dashscope_model = "qwen-plus"
        
        # 尝试初始化阿里云百炼API
        if Config.DASHSCOPE_API_KEY and DASHSCOPE_AVAILABLE:
            try:
                dashscope.api_key = Config.DASHSCOPE_API_KEY
                self.api_type = "dashscope"
                logger.info("阿里云百炼API初始化成功")
                return
            except Exception as e:
                logger.warning(f"阿里云百炼API初始化失败: {e}")
        
        logger.warning("未配置有效的阿里云百炼API，将使用预定义内容")
    
    def _generate_with_llm(self, prompt):
        """
        使用阿里云百炼API生成内容
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 生成的内容
        """
        try:
            if self.api_type == "dashscope":
                response = Generation.call(
                    model=self.dashscope_model,
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7
                )
                if response.status_code == 200:
                    return response.output.text
                else:
                    logger.error(f"阿里云百炼API调用失败: {response}")
                    return None
            
            return None
        except Exception as e:
            logger.error(f"阿里云百炼API调用出错: {e}")
            return None
    
    def retrieve_materials(self, learning_goal, level_analysis):
        """
        检索学习材料
        
        Args:
            learning_goal (str): 学习目标
            level_analysis (dict): 用户水平分析结果
            
        Returns:
            dict: 相关学习材料
        """
        # 根据学习目标和用户水平检索材料
        return self.learning_materials.get(learning_goal, {})
    
    def generate_explanation(self, level_analysis, materials, user_knowledge_graph):
        """
        生成解释内容
        
        Args:
            level_analysis (dict): 用户水平分析结果
            materials (dict): 学习材料
            user_knowledge_graph (dict): 用户知识图谱
            
        Returns:
            str: 个性化解释内容
        """
        # 如果API可用，使用大语言模型生成内容
        if self.api_type:
            try:
                level = level_analysis.get('level', 'beginner')
                concept = materials.get('concept', '未知概念')
                key_points = materials.get('key_points', [])
                
                prompt = f"""
                你是一个专业的编程教育专家，请根据以下信息生成个性化的学习内容：
                
                学习主题：{concept}
                学习者水平：{level}
                关键知识点：{', '.join(key_points)}
                学习者已掌握的知识：{json.dumps(user_knowledge_graph, ensure_ascii=False)}
                
                请生成适合该学习者水平的详细解释内容，要求：
                1. 如果是初学者，请用简单易懂的语言解释基础概念
                2. 如果是中级学习者，请深入讲解核心概念并提供示例
                3. 如果是高级学习者，请讲解高级特性和最佳实践
                4. 内容长度适中，大约200-300字
                5. 使用清晰的结构和适当的例子
                """
                
                explanation = self._generate_with_llm(prompt)
                if explanation:
                    return explanation
            except Exception as e:
                logger.error(f"使用LLM生成解释内容失败: {e}")
        
        # 回退到预定义内容
        level = level_analysis.get('level', 'beginner')
        content = materials.get('content', {})
        return content.get(level, "默认解释内容")
    
    def generate_exercises(self, level_analysis, materials):
        """
        生成练习题
        
        Args:
            level_analysis (dict): 用户水平分析结果
            materials (dict): 学习材料
            
        Returns:
            list: 个性化练习题列表
        """
        # 如果API可用，使用大语言模型生成练习题
        if self.api_type:
            try:
                level = level_analysis.get('level', 'beginner')
                concept = materials.get('concept', '未知概念')
                key_points = materials.get('key_points', [])
                
                prompt = f"""
                你是一个专业的编程教育专家，请为以下学习内容生成3道练习题：
                
                学习主题：{concept}
                学习者水平：{level}
                关键知识点：{', '.join(key_points)}
                
                请生成适合该学习者水平的练习题，要求：
                1. 如果是初学者，生成选择题和简单的编程题
                2. 如果是中级学习者，生成编程题和概念题
                3. 如果是高级学习者，生成复杂编程题和设计题
                4. 每道题都应该有明确的答案
                5. 以JSON格式返回，结构如下：
                [
                    {{
                        "type": "题目类型（multiple_choice/coding/conceptual）",
                        "question": "题目内容",
                        "options": ["选项A", "选项B", "选项C", "选项D"], （仅选择题需要）
                        "answer": "答案"
                    }}
                ]
                请只返回JSON格式的内容，不要包含其他文字。
                """
                
                exercises_json = self._generate_with_llm(prompt)
                if exercises_json:
                    try:
                        # 清理可能的额外文本
                        exercises_json = exercises_json.strip()
                        if exercises_json.startswith("```json"):
                            exercises_json = exercises_json[7:]
                        if exercises_json.endswith("```"):
                            exercises_json = exercises_json[:-3]
                        exercises_json = exercises_json.strip()
                        
                        # 尝试解析JSON
                        exercises = json.loads(exercises_json)
                        if isinstance(exercises, list):
                            return exercises[:3]  # 限制最多3道题
                    except json.JSONDecodeError as e:
                        logger.error(f"阿里云百炼API返回的练习题不是有效的JSON格式: {e}")
                        logger.error(f"返回内容: {exercises_json}")
            except Exception as e:
                logger.error(f"使用阿里云百炼API生成练习题失败: {e}")
        
        # 回退到预定义练习题
        level = level_analysis.get('level', 'beginner')
        exercises = materials.get('exercises', {})
        level_exercises = exercises.get(level, [])
        
        # 随机选择几道题以增加多样性
        if len(level_exercises) > 3:
            return random.sample(level_exercises, 3)
        return level_exercises
    
    def generate_interactive_response(self, message, context, topic, knowledge_graph):
        """
        生成交互式对话响应
        
        Args:
            message (str): 用户消息
            context (dict): 对话上下文
            topic (str): 学习主题
            knowledge_graph (dict): 用户知识图谱
            
        Returns:
            str: 生成的响应
        """
        # 如果API可用，使用大语言模型生成响应
        if self.api_type:
            try:
                # 构建提示词
                prompt = f"""
                你是一个专业的编程教育AI助手，正在与学习者进行交互式对话。请根据以下信息生成合适的响应：
                
                学习者消息：{message}
                学习主题：{topic}
                对话上下文：{json.dumps(context, ensure_ascii=False)}
                学习者知识图谱：{json.dumps(knowledge_graph, ensure_ascii=False)}
                
                请以教育性、友好和专业的语气回复学习者，要求：
                1. 准确理解学习者的问题或需求
                2. 提供清晰、有帮助的回答
                3. 如果是编程相关问题，可以提供示例代码
                4. 适当引导学习者深入思考
                5. 回答长度适中，不要太长
                6. 如果学习者的问题与当前主题无关，请礼貌地引导回主题
                7. 如果学习者表达了困惑，请耐心解释并提供额外示例
                8. 鼓励学习者继续学习和探索
                """
                
                response = self._generate_with_llm(prompt)
                if response:
                    return response.strip()
            except Exception as e:
                logger.error(f"使用LLM生成交互式响应失败: {e}")
        
        # 回退到预定义响应
        return self._generate_fallback_response(message, topic)
    
    def _generate_fallback_response(self, message, topic):
        """
        生成回退响应
        
        Args:
            message (str): 用户消息
            topic (str): 学习主题
            
        Returns:
            str: 回退响应
        """
        # 简单的关键词匹配和响应
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower or "你好" in message_lower:
            return "你好！我是你的AI学习助手。有什么我可以帮助你的吗？"
        
        if "python" in message_lower:
            return "Python是一种易于学习且功能强大的编程语言。它广泛应用于Web开发、数据分析、人工智能等领域。你想了解Python的哪个方面呢？"
        
        if "变量" in message_lower:
            return "变量是存储数据的容器。在Python中，你可以这样定义变量：name = 'Alice' 或 age = 10。变量名应该具有描述性，让人一看就知道它的用途。"
        
        if "函数" in message_lower:
            return "函数是一段可重复使用的代码块。你可以这样定义函数：\n```python\ndef greet(name):\n    return f'你好, {name}!'\n\n# 调用函数\nprint(greet('小明'))\n```\n函数可以接收参数并返回值。"
        
        if "循环" in message_lower or "loop" in message_lower:
            return "循环用于重复执行代码块。Python中有两种主要的循环：for循环和while循环。\n```python\n# for循环示例\nfor i in range(5):\n    print(i)\n\n# while循环示例\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n```"
        
        if "help" in message_lower or "帮助" in message_lower:
            return "我可以帮助你学习编程知识。你可以问我任何关于编程的问题，比如Python语法、数据结构、算法等。你也可以告诉我你想学习的主题，我会为你提供相关的内容。"
        
        # 默认响应
        return "我是你的AI学习助手。请告诉我你想学习什么内容，我会尽力帮助你。"

    def get_available_topics(self):
        """
        获取所有可用的学习主题
        
        Returns:
            list: 学习主题列表
        """
        return list(self.learning_materials.keys())
    
    def get_topic_info(self, topic):
        """
        获取特定主题的信息
        
        Args:
            topic (str): 主题名称
            
        Returns:
            dict: 主题信息
        """
        if topic in self.learning_materials:
            material = self.learning_materials[topic]
            return {
                "concept": material["concept"],
                "key_points": material["key_points"]
            }
        return None