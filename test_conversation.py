"""
测试改进后的 Agent 对话
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core.medical_agent import MedicalAgent

def test_agent_conversation():
    """模拟完整对话流程"""
    print("=" * 70)
    print("测试医疗问诊 Agent - 改进版（带信息收集判断）")
    print("=" * 70)
    
    # 创建 Agent
    agent = MedicalAgent(llm_type="zhipu")
    
    # 模拟对话
    conversation = [
        "头疼啊",
        "前额疼",
        "持续三天了",
        "跳痛",
        "没有",
    ]
    
    for i, user_input in enumerate(conversation):
        print(f"\n{'='*70}")
        print(f"第 {i+1} 轮对话")
        print(f"{'='*70}")
        print(f"🧑 患者: {user_input}")
        
        try:
            response = agent.chat(user_input)
            print(f"🤖 医生: {response}")
            
            # 显示收集到的信息
            print(f"\n📋 已收集信息: {agent.patient_info}")
            
            # 如果给出建议，提前结束
            if "建议" in response and "可能的原因" in response:
                print(f"\n{'='*70}")
                print("✅ Agent 已给出综合建议，对话结束")
                break
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("完整对话历史:")
    print(f"{'='*70}")
    for msg in agent.memory:
        role = "🧑" if msg['role'] == 'user' else "🤖"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"{role} {msg['role']}: {content}")


if __name__ == "__main__":
    test_agent_conversation()
