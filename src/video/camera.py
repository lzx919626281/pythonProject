#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摄像头模块
"""

import cv2
import threading
import queue

class Camera:
    def __init__(self, config):
        """初始化摄像头"""
        self.config = config
        self.camera_index = config['camera_index']
        self.width = config['width']
        self.height = config['height']
        self.fps = config['fps']
        
        # 初始化摄像头
        self.cap = None
        self.running = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.thread = None
    
    def start(self):
        """启动摄像头"""
        try:
            # 打开摄像头
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            if not self.cap.isOpened():
                print("无法打开摄像头")
                return False
            
            # 启动线程捕捉画面
            self.running = True
            self.thread = threading.Thread(target=self._capture_frames)
            self.thread.daemon = True
            self.thread.start()
            
            print("摄像头启动成功")
            return True
            
        except Exception as e:
            print(f"摄像头启动失败: {e}")
            return False
    
    def _capture_frames(self):
        """捕捉摄像头画面"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # 处理画面（这里可以添加人脸识别、表情识别等功能）
                processed_frame = self._process_frame(frame)
                
                # 将处理后的画面放入队列
                if not self.frame_queue.full():
                    self.frame_queue.put(processed_frame)
                else:
                    # 队列满了，丢弃旧帧
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put(processed_frame)
                    except queue.Empty:
                        pass
    
    def _process_frame(self, frame):
        """处理摄像头画面"""
        # 这里可以添加各种图像处理功能
        # 例如：人脸识别、表情识别、姿态估计等
        
        # 简单的处理：添加边框
        processed_frame = cv2.copyMakeBorder(
            frame, 
            10, 10, 10, 10, 
            cv2.BORDER_CONSTANT, 
            value=(0, 255, 0)
        )
        
        return processed_frame
    
    def get_frame(self):
        """获取摄像头画面"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """停止摄像头"""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
        
        print("摄像头已停止")