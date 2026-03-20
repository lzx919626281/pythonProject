#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话管理模块
"""

import os
import json
from collections import deque

class DialogueManager:
    def __init__(self, config):
        """初始化对话管理器"""
        self.config = config
        self.max_history = config['max_history']
        self.model_path = config['model_path']
        
        # 对话历史
        self.history = deque(maxlen=self.max_history)
        
        # 初始化对话规则
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """加载对话规则"""
        # 简单的基于规则的对话系统
        rules = {
            # 问候
            'greeting': {
                'patterns': ['你好', '哈喽', '嗨', '早上好', '下午好', '晚上好'],
                'responses': ['你好！', '哈喽，有什么可以帮助你的吗？', '嗨，很高兴见到你！', '早上好！今天过得怎么样？', '下午好！有什么我可以帮忙的吗？', '晚上好！今天过得如何？']
            },
            # 自我介绍
            'self_intro': {
                'patterns': ['你是谁', '你叫什么', '介绍一下你自己', '你是什么'],
                'responses': ['我是你的数字助手，很高兴为你服务！', '我是一个智能数字人，可以和你聊天、回答问题。', '你好，我是你的数字伙伴，随时为你提供帮助。']
            },
            # 天气
            'weather': {
                'patterns': ['天气怎么样', '今天天气如何', '明天天气', '天气'],
                'responses': ['抱歉，我目前还不能提供实时天气信息。', '你可以通过天气应用查看最新的天气情况。', '天气不错呢，适合出去走走！']
            },
            # 时间
            'time': {
                'patterns': ['现在几点', '几点了', '当前时间', '时间'],
                'responses': ['抱歉，我目前还不能提供实时时间。', '你可以查看电脑右下角的时间。', '现在应该是你需要休息的时间了！']
            },
            # 帮助
            'help': {
                'patterns': ['帮助', '怎么用', '功能', '能做什么'],
                'responses': ['我可以和你聊天、回答问题，还可以通过摄像头看到你。', '你可以问我问题，或者和我随便聊聊。', '我是你的数字助手，随时为你服务！']
            },
            # 再见
            'goodbye': {
                'patterns': ['再见', '拜拜', '下次见', '回头见'],
                'responses': ['再见！', '拜拜，期待下次和你聊天！', '回头见，有什么需要随时告诉我！']
            }
        }
        return rules
    
    def process(self, text):
        """处理用户输入并生成响应"""
        # 添加到对话历史
        self.history.append({'role': 'user', 'content': text})
        
        # 处理输入
        response = self._generate_response(text)
        
        # 添加到对话历史
        self.history.append({'role': 'assistant', 'content': response})
        
        return response
    
    def _generate_response(self, text):
        """生成响应"""
        # 匹配规则
        for intent, data in self.rules.items():
            for pattern in data['patterns']:
                if pattern in text:
                    import random
                    return random.choice(data['responses'])
        
        # 没有匹配到规则，返回默认响应
        default_responses = [
            '我不太明白你的意思，能再说一遍吗？',
            '抱歉，我还在学习中，不太理解你说的话。',
            '你能换个方式表达吗？',
            '有意思的观点，能详细说说吗？',
            '我会努力学习，争取更好地理解你。'
        ]
        
        import random
        return random.choice(default_responses)
    
    def get_history(self):
        """获取对话历史"""
        return list(self.history)
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()