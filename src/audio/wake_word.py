#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音唤醒模块
"""

import os
import time
import numpy as np
import pyaudio

class WakeWordDetector:
    def __init__(self, config):
        """初始化唤醒词检测器"""
        self.config = config
        self.audio_threshold = config['audio_threshold']
        self.model_path = config['model_path']
        
        # 音频参数
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        self.channels = 1
        
        # 初始化音频流
        self.pa = pyaudio.PyAudio()
        self.stream = None
        
        # 唤醒词模型（这里使用简单的关键词检测，实际项目中可以使用更复杂的模型）
        self.wake_words = ["你好", "嘿", "数字人"]
    
    def _detect_speech(self, frame):
        """检测语音活动（基于能量）"""
        # 将音频帧转换为numpy数组
        audio_data = np.frombuffer(frame, dtype=np.int16)
        # 计算能量
        energy = np.sum(np.square(audio_data)) / len(audio_data)
        # 基于能量阈值判断是否有语音
        return energy > self.audio_threshold * 10000
    
    def detect(self):
        """检测唤醒词"""
        try:
            # 打开音频流
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frame_size
            )
            
            print("正在监听唤醒词...")
            
            # 收集音频数据
            frames = []
            voiced_frames = []
            started = False
            
            while True:
                # 读取音频帧
                frame = self.stream.read(self.frame_size)
                frames.append(frame)
                
                # 检测语音活动
                is_speech = self._detect_speech(frame)
                
                if is_speech:
                    if not started:
                        started = True
                        print("检测到语音...")
                    voiced_frames.append(frame)
                else:
                    if started:
                        # 语音结束，检查是否包含唤醒词
                        if len(voiced_frames) > 0:
                            # 这里简化处理，实际项目中应该使用语音识别或专门的唤醒词模型
                            # 这里模拟检测到唤醒词
                            if self._simulate_wake_word_detection():
                                print("检测到唤醒词！")
                                return True
                        # 重置
                        started = False
                        voiced_frames = []
                
                # 限制帧数量，避免内存占用过高
                if len(frames) > 100:
                    frames = frames[-50:]
                    
        except Exception as e:
            print(f"唤醒词检测出错: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
        
        return False
    
    def _simulate_wake_word_detection(self):
        """模拟唤醒词检测（实际项目中应该使用真实的模型）"""
        # 这里使用随机数模拟检测结果，实际项目中应该使用语音识别或专门的唤醒词模型
        import random
        return random.random() > 0.7  # 30%的概率检测到唤醒词
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'pa'):
            self.pa.terminate()