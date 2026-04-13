"""
测试合并后的知识库
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.tools.knowledge_base import MedicalKnowledgeBase

def test_merged_kb():
    """测试合并后的知识库"""
    print("=" * 70)
    print("测试合并知识库")
    print("=" * 70)
    
    kb = MedicalKnowledgeBase()
    
    # 测试各种查询
    test_queries = [
        "高血压能吃党参吗",
        "心力衰竭是什么原因",
        "心律失常怎么办",
        "肺炎怎么护理",
        "冠心病注意事项",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"查询: {query}")
        print(f"{'='*70}")
        
        results = kb.search(query, top_k=2)
        
        if results:
            for i, item in enumerate(results, 1):
                print(f"\n【结果{i}】{item['department']}")
                print(f"标题: {item['title'][:60]}...")
                print(f"回答: {item['answer'][:150]}...")
        else:
            print("未找到相关结果")
    
    print(f"\n{'='*70}")
    print(f"✅ 知识库测试完成")
    print(f"{'='*70}")

if __name__ == "__main__":
    test_merged_kb()
