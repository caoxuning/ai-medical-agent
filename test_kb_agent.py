"""
测试带知识库的 Agent
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core.medical_agent import MedicalAgent

def test_with_knowledge_base():
    """测试带知识库的 Agent"""
    print("=" * 70)
    print("测试医疗问诊 Agent - 带医学知识库")
    print("=" * 70)
    
    # 创建 Agent
    agent = MedicalAgent(llm_type="zhipu")
    
    # 模拟对话 - 高血压相关
    conversation = [
        "我高血压能吃党参吗",
        "血压有点高",
        "最近体检发现的",
    ]
    
    for i, user_input in enumerate(conversation):
        print(f"\n{'='*70}")
        print(f"第 {i+1} 轮对话")
        print(f"{'='*70}")
        print(f"🧑 患者: {user_input}")
        
        try:
            response = agent.chat(user_input)
            print(f"🤖 医生: {response}")
            
            # 如果给出建议，提前结束
            if "根据医学知识库" in response or "建议就医" in response:
                print(f"\n{'='*70}")
                print("✅ Agent 已给出基于知识库的建议")
                break
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"📋 患者信息: {agent.patient_info}")


if __name__ == "__main__":
    test_with_knowledge_base()
