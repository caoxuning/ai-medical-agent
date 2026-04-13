"""
Agent 工具集合
定义 Agent 可调用的各种工具
"""

from typing import Dict, Any, Callable
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """工具基类"""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    def run(self, input_str: str) -> str:
        """执行工具"""
        pass


class AskUserTool(BaseTool):
    """向用户提问工具"""
    
    name = "ask_user"
    description = "向患者询问更多信息，用于收集症状细节"
    
    def run(self, question: str) -> str:
        """
        向用户提问
        
        Args:
            question: 要问的问题
            
        Returns:
            问题内容（直接展示给用户）
        """
        return question


class GiveAdviceTool(BaseTool):
    """给出建议工具"""
    
    name = "give_advice"
    description = "基于当前信息给出医疗建议"
    
    def run(self, advice: str) -> str:
        """
        给出医疗建议
        
        Args:
            advice: 建议内容
            
        Returns:
            格式化后的建议
        """
        return f"{advice}\n\n（以上建议仅供参考，不能替代专业医生的诊断）"


class SearchKnowledgeTool(BaseTool):
    """知识库查询工具 - 接入真实医学知识库"""
    
    name = "search_knowledge"
    description = "查询医学知识库，获取疾病、症状、药物等专业信息（基于1800+真实医疗问答数据）"
    
    def __init__(self):
        # 延迟加载知识库
        self._kb = None
    
    def _get_kb(self):
        """获取知识库实例"""
        if self._kb is None:
            from .knowledge_base import get_knowledge_base
            self._kb = get_knowledge_base()
        return self._kb
    
    def run(self, query: str) -> str:
        """
        查询知识库
        
        Args:
            query: 查询关键词
            
        Returns:
            查询结果
        """
        try:
            kb = self._get_kb()
            return kb.get_answer(query)
        except Exception as e:
            return f"知识库查询失败: {e}。建议咨询专业医生。"


class RecordSymptomTool(BaseTool):
    """记录症状工具"""
    
    name = "record_symptom"
    description = "记录患者症状信息"
    
    def __init__(self, patient_info=None):
        self.patient_info = patient_info
    
    def run(self, symptom_info: str) -> str:
        """
        记录症状
        
        Args:
            symptom_info: 症状描述
            
        Returns:
            确认信息
        """
        if self.patient_info:
            self.patient_info.add_symptom(symptom_info)
        return f"已记录症状: {symptom_info}"


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register(AskUserTool())
        self.register(GiveAdviceTool())
        self.register(SearchKnowledgeTool())
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> BaseTool:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """列出所有工具"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    def get_tool_descriptions(self) -> str:
        """获取工具描述文本（用于 Prompt）"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)


# 便捷函数
def create_default_tools() -> ToolRegistry:
    """创建默认工具集"""
    return ToolRegistry()
