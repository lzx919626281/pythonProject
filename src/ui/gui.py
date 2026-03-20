#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户界面模块
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import queue
import time

class GUI:
    def __init__(self):
        """初始化GUI"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("数字人系统")
        self.root.geometry("800x600")
        
        # 设置窗口关闭时的处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 创建界面组件
        self._create_widgets()
        
        # 运行状态
        self.running = False
        
        # 创建更新队列
        self.update_queue = queue.Queue()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建摄像头画面区域
        camera_frame = ttk.LabelFrame(main_frame, text="摄像头", padding="10")
        camera_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 摄像头画面标签
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # 创建对话区域
        dialogue_frame = ttk.LabelFrame(main_frame, text="对话", padding="10")
        dialogue_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # 对话历史文本框
        self.dialogue_text = tk.Text(dialogue_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.dialogue_text.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # 系统状态标签
        self.status_label = ttk.Label(dialogue_frame, text="状态: 等待唤醒...", foreground="green")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
    
    def start(self):
        """启动GUI"""
        self.running = True
        # 启动更新处理线程
        self.update_thread = threading.Thread(target=self._process_updates)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # 启动主循环（在主线程中）
        self._run_gui()
    
    def _run_gui(self):
        """运行GUI主循环"""
        while self.running:
            try:
                self.root.update_idletasks()
                self.root.update()
            except Exception as e:
                print(f"GUI更新出错: {e}")
                break
    
    def _process_updates(self):
        """处理更新队列"""
        while self.running:
            try:
                if not self.update_queue.empty():
                    update_type, *args = self.update_queue.get()
                    if update_type == "frame":
                        self._update_frame(*args)
                    elif update_type == "message":
                        self._add_message(*args)
                    elif update_type == "status":
                        self._set_status(*args)
                time.sleep(0.01)
            except Exception as e:
                print(f"处理更新队列出错: {e}")
                break
    
    def _update_frame(self, frame):
        """更新摄像头画面（内部方法，在GUI线程中调用）"""
        try:
            # 转换OpenCV图像到PIL图像
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
            # 调整图像大小以适应窗口
            width = self.camera_label.winfo_width()
            height = self.camera_label.winfo_height()
            if width > 0 and height > 0:
                image = image.resize((width, height), Image.LANCZOS)
            
            # 转换为Tkinter图像
            photo = ImageTk.PhotoImage(image)
            
            # 更新标签
            self.camera_label.config(image=photo)
            self.camera_label.image = photo  # 保持引用，防止被垃圾回收
        except Exception as e:
            print(f"更新摄像头画面出错: {e}")
    
    def update_frame(self, frame):
        """更新摄像头画面"""
        if not self.running:
            return
        self.update_queue.put(("frame", frame))
    
    def _add_message(self, sender, message):
        """添加对话消息（内部方法，在GUI线程中调用）"""
        try:
            self.dialogue_text.config(state=tk.NORMAL)
            self.dialogue_text.insert(tk.END, f"{sender}: {message}\n\n")
            self.dialogue_text.see(tk.END)  # 滚动到最新消息
            self.dialogue_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"添加消息出错: {e}")
    
    def add_message(self, sender, message):
        """添加对话消息"""
        if not self.running:
            return
        self.update_queue.put(("message", sender, message))
    
    def _set_status(self, status):
        """设置系统状态（内部方法，在GUI线程中调用）"""
        try:
            self.status_label.config(text=f"状态: {status}")
        except Exception as e:
            print(f"设置状态出错: {e}")
    
    def set_status(self, status):
        """设置系统状态"""
        if not self.running:
            return
        self.update_queue.put(("status", status))
    
    def stop(self):
        """停止GUI"""
        self.running = False
        if hasattr(self, 'gui_thread'):
            self.gui_thread.join(timeout=2)
        try:
            self.root.destroy()
        except Exception as e:
            print(f"关闭GUI出错: {e}")
    
    def _on_close(self):
        """窗口关闭事件处理"""
        self.running = False
        self.root.destroy()