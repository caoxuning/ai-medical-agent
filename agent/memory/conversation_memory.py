"""
Agent 记忆管理模块
管理对话历史和患者信息
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class ConversationMemory:
    """
    对话记忆管理
    
    功能:
    - 存储多轮对话历史
    - 支持上下文窗口管理
    - 持久化存储（可选）
    """
    
    def __init__(self, max_context_length: int = 10):
        self.max_context_length = max_context_length
        self.messages: List[Dict[str, Any]] = []
        self.session_id: str = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_context()
    
    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_context()
    
    def add_system_message(self, content: str):
        """添加系统消息（如工具执行结果）"""
        self.messages.append({
            "role": "system",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._trim_context()
    
    def get_context(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取最近 n 条对话上下文
        
        Args:
            n: 获取条数，None 则返回全部
        """
        if n is None:
            return self.messages
        return self.messages[-n:]
    
    def get_formatted_context(self, n: int = 5) -> str:
        """
        获取格式化的对话历史字符串
        
        Args:
            n: 最近 n 轮对话
        """
        context = ""
        for msg in self.messages[-n:]:
            if msg["role"] == "user":
                context += f"患者: {msg['content']}\n"
            elif msg["role"] == "assistant":
                context += f"医生: {msg['content']}\n"
            elif msg["role"] == "system":
                context += f"[系统] {msg['content']}\n"
        return context.strip()
    
    def _trim_context(self):
        """修剪上下文，保持长度限制"""
        if len(self.messages) > self.max_context_length * 2:
            # 保留最近 max_context_length 轮对话
            self.messages = self.messages[-self.max_context_length * 2:]
    
    def clear(self):
        """清空记忆"""
        self.messages = []
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        data = {
            "session_id": self.session_id,
            "messages": self.messages
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.session_id = data.get("session_id", self._generate_session_id())
        self.messages = data.get("messages", [])


class PatientInfo:
    """
    患者信息管理
    
    管理患者的基本信息和症状信息
    支持槽位填充（Slot Filling）
    """
    
    def __init__(self):
        self.info: Dict[str, Any] = {}
        self.symptoms: List[str] = []
        self.extracted_slots: Dict[str, Any] = {}
    
    def update(self, key: str, value: Any):
        """更新患者信息"""
        self.info[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取患者信息"""
        return self.info.get(key, default)
    
    def add_symptom(self, symptom: str):
        """添加症状"""
        if symptom not in self.symptoms:
            self.symptoms.append(symptom)
    
    def get_symptoms(self) -> List[str]:
        """获取所有症状"""
        return self.symptoms
    
    def fill_slot(self, slot_name: str, value: Any):
        """填充槽位"""
        self.extracted_slots[slot_name] = value
    
    def get_slot(self, slot_name: str) -> Any:
        """获取槽位值"""
        return self.extracted_slots.get(slot_name)
    
    def get_missing_slots(self, required_slots: List[str]) -> List[str]:
        """获取未填充的必需槽位"""
        return [slot for slot in required_slots if slot not in self.extracted_slots]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "info": self.info,
            "symptoms": self.symptoms,
            "slots": self.extracted_slots
        }
    
    def get_summary(self) -> str:
        """获取患者信息摘要"""
        summary = "患者信息:\n"
        
        if self.info:
            for key, value in self.info.items():
                summary += f"  {key}: {value}\n"
        
        if self.symptoms:
            summary += f"  症状: {', '.join(self.symptoms)}\n"
        
        if self.extracted_slots:
            summary += "  已提取信息:\n"
            for key, value in self.extracted_slots.items():
                summary += f"    - {key}: {value}\n"
        
        return summary
    
    def clear(self):
        """清空信息"""
        self.info = {}
        self.symptoms = []
        self.extracted_slots = {}
