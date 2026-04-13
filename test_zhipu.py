"""
测试智谱 AI 接入
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core.medical_agent import ZhipuLLM

def test_zhipu():
    """测试智谱 AI 调用"""
    print("=" * 50)
    print("测试智谱 AI 接入")
    print("=" * 50)
    
    # 检查 API Key
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ ZHIPU_API_KEY 未设置")
        print("请设置环境变量: $env:ZHIPU_API_KEY='your-key'")
        return
    
    print(f"✅ API Key 已设置: {api_key[:10]}...")
    
    try:
        # 初始化 LLM
        llm = ZhipuLLM()
        print("✅ 智谱 LLM 初始化成功")
        
        # 测试生成
        prompt = """你是一位医疗助手。患者说："我最近头疼，已经持续三天了"

请分析：
1. 患者的主要症状是什么？
2. 你需要询问哪些信息？
3. 下一步应该怎么做？

请简洁回答。"""
        
        print("\n📝 发送 Prompt:")
        print("-" * 50)
        print(prompt[:200] + "...")
        print("-" * 50)
        
        print("\n🤖 智谱 AI 回复:")
        response = llm.generate(prompt)
        print(response)
        
        print("\n" + "=" * 50)
        print("✅ 测试完成！智谱 AI 接入正常")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_zhipu()
