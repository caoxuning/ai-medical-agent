"""
医学知识库检索系统
基于关键词匹配的简单检索（演示用）
"""
import json
import os
from typing import List, Dict, Any


class MedicalKnowledgeBase:
    """医学知识库"""
    
    def __init__(self, knowledge_file: str = None):
        # 自动查找知识库文件
        if knowledge_file is None:
            # 尝试多个可能的路径
            possible_paths = [
                "data/medical_knowledge/knowledge_base.json",
                "../data/medical_knowledge/knowledge_base.json",
                "../../data/medical_knowledge/knowledge_base.json",
                os.path.join(os.path.dirname(__file__), "../../data/medical_knowledge/knowledge_base.json"),
                os.path.join(os.path.dirname(__file__), "../../../data/medical_knowledge/knowledge_base.json"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    knowledge_file = path
                    break
        
        self.knowledge_file = knowledge_file
        self.knowledge: List[Dict[str, Any]] = []
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载知识库"""
        if not os.path.exists(self.knowledge_file):
            print(f"⚠️ 知识库文件不存在: {self.knowledge_file}")
            return
        
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
            print(f"✅ 知识库加载完成: {len(self.knowledge)} 条记录")
        except Exception as e:
            print(f"❌ 知识库加载失败: {e}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            query: 查询关键词
            top_k: 返回结果数量
            
        Returns:
            相关知识条目列表
        """
        if not self.knowledge:
            return []
        
        # 关键词匹配（简单实现）
        keywords = self._extract_keywords(query)
        
        scored_results = []
        for item in self.knowledge:
            score = self._calculate_score(item, keywords)
            if score > 0:
                scored_results.append((score, item))
        
        # 按分数排序，返回前 top_k
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_results[:top_k]]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 医疗相关关键词
        medical_keywords = [
            "头疼", "头痛", "发烧", "发热", "咳嗽", "感冒", "流感",
            "肚子", "腹痛", "胃痛", "恶心", "呕吐", "腹泻",
            "高血压", "血压", "糖尿病", "血糖",
            "失眠", "头晕", "乏力", "疲劳",
            "过敏", "皮疹", "瘙痒",
            "骨折", "扭伤", "疼痛",
            "月经", "妇科", "产科", "怀孕",
            "儿科", "儿童", "婴儿", "发烧",
            "肿瘤", "癌症", "化疗",
            "手术", "外伤", "出血",
        ]
        
        found_keywords = []
        for kw in medical_keywords:
            if kw in text:
                found_keywords.append(kw)
        
        return found_keywords
    
    def _calculate_score(self, item: Dict[str, Any], keywords: List[str]) -> int:
        """计算匹配分数"""
        score = 0
        text = item.get("text", "")
        title = item.get("title", "")
        question = item.get("question", "")
        answer = item.get("answer", "")
        
        for kw in keywords:
            # 标题匹配权重最高
            if kw in title:
                score += 10
            # 问题匹配
            if kw in question:
                score += 5
            # 回答匹配
            if kw in answer:
                score += 3
            # 文本匹配
            if kw in text:
                score += 1
        
        return score
    
    def get_answer(self, query: str) -> str:
        """
        获取回答
        
        Args:
            query: 查询问题
            
        Returns:
            格式化的回答
        """
        results = self.search(query, top_k=2)
        
        if not results:
            return "未找到相关医学知识。建议咨询专业医生。"
        
        response = "根据医学知识库，为您找到以下相关信息：\n\n"
        
        for i, item in enumerate(results, 1):
            response += f"【参考{i}】{item['department']}\n"
            response += f"问题：{item['question'][:80]}...\n"
            response += f"回答：{item['answer'][:200]}...\n\n"
        
        response += "（以上信息仅供参考，不能替代专业医生的诊断）"
        return response


# 单例模式
_kb_instance = None

def get_knowledge_base() -> MedicalKnowledgeBase:
    """获取知识库实例"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = MedicalKnowledgeBase()
    return _kb_instance


if __name__ == "__main__":
    # 测试
    kb = MedicalKnowledgeBase()
    
    test_queries = [
        "高血压能吃党参吗",
        "头疼怎么办",
        "感冒发烧",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")
        print(kb.get_answer(query))
