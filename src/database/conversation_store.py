#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话存储模块
"""

import os
import sqlite3
import datetime

class ConversationStore:
    def __init__(self, config):
        """初始化对话存储"""
        self.config = config
        self.db_path = config['path']
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建对话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
        ''')
        
        # 创建学习表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            response TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            usage_count INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_input, response):
        """保存对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO conversations (user_input, response, timestamp) VALUES (?, ?, ?)",
            (user_input, response, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def get_conversations(self, limit=100):
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, user_input, response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        conversations = cursor.fetchall()
        conn.close()
        
        return conversations
    
    def learn_from_conversation(self):
        """从对话中学习"""
        # 这里可以实现更复杂的学习逻辑
        # 例如：分析对话模式，提取常见问题和回答
        # 这里我们简单实现一个基于频率的学习方法
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 分析最近的对话
        cursor.execute(
            "SELECT user_input, response FROM conversations ORDER BY timestamp DESC LIMIT 10"
        )
        
        recent_conversations = cursor.fetchall()
        
        for user_input, response in recent_conversations:
            # 检查是否已经存在类似的模式
            cursor.execute(
                "SELECT id, confidence, usage_count FROM learning WHERE pattern LIKE ?",
                (f"%{user_input}%",)
            )
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有模式
                id_, confidence, usage_count = existing
                new_confidence = min(confidence + 0.1, 1.0)
                new_usage_count = usage_count + 1
                
                cursor.execute(
                    "UPDATE learning SET confidence = ?, usage_count = ? WHERE id = ?",
                    (new_confidence, new_usage_count, id_)
                )
            else:
                # 添加新模式
                cursor.execute(
                    "INSERT INTO learning (pattern, response, confidence, usage_count) VALUES (?, ?, ?, ?)",
                    (user_input, response, 0.5, 1)
                )
        
        conn.commit()
        conn.close()
    
    def get_learned_responses(self, query):
        """获取学习到的响应"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT response, confidence FROM learning WHERE pattern LIKE ? ORDER BY confidence DESC LIMIT 5",
            (f"%{query}%",)
        )
        
        responses = cursor.fetchall()
        conn.close()
        
        return responses
    
    def clear_conversations(self):
        """清空对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()
    
    def clear_learning(self):
        """清空学习数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM learning")
        conn.commit()
        conn.close()