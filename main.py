#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数字人系统主程序
"""

import os
import sys
import time
import logging
import yaml
import threading
from src.audio.wake_word import WakeWordDetector
from src.audio.speech_recognition import SpeechRecognizer
from src.video.camera import Camera
from src.nlp.dialogue_manager import DialogueManager
from src.database.conversation_store import ConversationStore
from src.ui.gui import GUI

class DigitalHuman:
    def __init__(self):
        # 加载配置
        self.config = self.load_config()
        
        # 初始化日志
        self.setup_logging()
        
        # 初始化各个模块
        self.wake_word_detector = WakeWordDetector(self.config['wake_word'])
        self.speech_recognizer = SpeechRecognizer(self.config['speech_recognition'])
        self.camera = Camera(self.config['video'])
        self.dialogue_manager = DialogueManager(self.config['nlp'])
        self.conversation_store = ConversationStore(self.config['database'])
        
        # GUI将在主线程中初始化
        self.gui = None
        
        self.logger.info("数字人系统初始化完成")
    
    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config['system']['log_level'], logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('digital_human.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DigitalHuman')
    
    def run_core(self):
        """运行数字人系统核心功能"""
        self.logger.info("数字人系统核心功能启动")
        
        # 启动摄像头
        self.camera.start()
        
        try:
            while True:
                # 检测唤醒词
                self.logger.info("等待唤醒词...")
                if self.wake_word_detector.detect():
                    self.logger.info("检测到唤醒词")
                    
                    # 唤醒后开始对话
                    self.gui.set_status("对话中...")
                    
                    # 语音识别
                    self.logger.info("开始语音识别...")
                    text = self.speech_recognizer.recognize()
                    
                    if text:
                        self.logger.info(f"识别到语音: {text}")
                        
                        # 处理对话
                        response = self.dialogue_manager.process(text)
                        self.logger.info(f"生成响应: {response}")
                        
                        # 存储对话
                        self.conversation_store.save_conversation(text, response)
                        
                        # 学习对话
                        self.conversation_store.learn_from_conversation()
                        
                        # 显示对话
                        self.gui.add_message("用户", text)
                        self.gui.add_message("数字人", response)
                        
                        # 语音合成
                        self.speech_recognizer.speak(response)
                    
                    self.gui.set_status("等待唤醒...")
                
                # 显示摄像头画面
                frame = self.camera.get_frame()
                if frame is not None:
                    self.gui.update_frame(frame)
                
                # 小延迟，避免CPU占用过高
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            self.logger.info("系统被用户中断")
        finally:
            # 清理资源
            self.camera.stop()
            self.logger.info("数字人系统核心功能已停止")

if __name__ == "__main__":
    # 创建数字人实例
    digital_human = DigitalHuman()
    
    # 在主线程中初始化GUI
    digital_human.gui = GUI()
    
    # 启动核心功能线程
    core_thread = threading.Thread(target=digital_human.run_core)
    core_thread.daemon = True
    core_thread.start()
    
    try:
        # 启动GUI（主线程）
        digital_human.gui.start()
    except KeyboardInterrupt:
        pass
    finally:
        # 停止GUI
        digital_human.gui.stop()
        digital_human.logger.info("数字人系统已停止")