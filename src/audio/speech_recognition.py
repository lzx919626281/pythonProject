#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音识别模块
"""

import speech_recognition as sr
import pyttsx3
import pyaudio

class SpeechRecognizer:
    def __init__(self, config):
        """初始化语音识别器"""
        self.config = config
        self.language = config['language']
        self.timeout = config['timeout']
        self.phrase_time_limit = config['phrase_time_limit']
        
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        
        # 初始化语音合成器
        self.engine = pyttsx3.init()
        
        # 设置语音合成参数
        self._setup_tts()
    
    def _setup_tts(self):
        """设置语音合成参数"""
        # 获取可用的语音
        voices = self.engine.getProperty('voices')
        
        # 选择中文语音（如果可用）
        for voice in voices:
            if 'zh' in voice.id or 'Chinese' in voice.name:
                self.engine.setProperty('voice', voice.id)
                break
        
        # 设置语速
        self.engine.setProperty('rate', 150)
        
        # 设置音量
        self.engine.setProperty('volume', 1.0)
    
    def recognize(self):
        """识别语音并转换为文本"""
        with sr.Microphone() as source:
            print("请说话...")
            
            # 调整麦克风灵敏度
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # 监听语音
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout, 
                    phrase_time_limit=self.phrase_time_limit
                )
                
                # 使用Google Web Speech API进行识别
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"识别结果: {text}")
                return text
                
            except sr.WaitTimeoutError:
                print("识别超时")
                return None
            except sr.UnknownValueError:
                print("无法识别语音")
                return None
            except sr.RequestError as e:
                print(f"请求错误: {e}")
                return None
    
    def speak(self, text):
        """将文本转换为语音"""
        try:
            print(f"数字人: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"语音合成出错: {e}")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'engine'):
            self.engine.stop()