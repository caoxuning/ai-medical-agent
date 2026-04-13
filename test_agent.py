"""
直接测试 Agent 对话
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core.medical_agent import MedicalAgent

def test_agent():
    """测试 Agent 对话"""
    print("=" * 60)
    print("测试医疗问诊 Agent")
    print("=" * 60)
    
    # 创建 Agent
    agent = MedicalAgent(llm_type="zhipu")
    
    # 模拟对话
    test_inputs = [
        "头疼啊",
        "前额疼，已经三天了",
        "还有点恶心",
    ]
    
    for user_input in test_inputs:
        print(f"\n🧑 患者: {user_input}")
        print("-" * 60)
        
        try:
            response = agent.chat(user_input)
            print(f"🤖 医生: {response}")
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("对话完成")
    print("=" * 60)
    print(f"\n患者信息: {agent.patient_info}")
    print(f"\n对话历史:")
    for msg in agent.memory:
        print(f"  {msg['role']}: {msg['content'][:50]}...")


if __name__ == "__main__":
    test_agent()
