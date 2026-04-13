"""
Agent 启动脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core.medical_agent import MedicalAgent


def run_interactive():
    """交互式运行 Agent"""
    print("=" * 60)
    print("  医疗问诊 Agent - 基于 ReAct 架构")
    print("=" * 60)
    print("\n命令:")
    print("  - 输入症状描述开始问诊")
    print("  - 'reset' 重置对话")
    print("  - 'info' 查看患者信息")
    print("  - 'exit' 退出")
    print("=" * 60)
    
    # 选择 LLM 类型
    import os
    if os.getenv("ZHIPU_API_KEY"):
        print("\n🔧 检测到 ZHIPU_API_KEY，使用智谱 AI")
        llm_type = "zhipu"
    else:
        print("\n🔧 未检测到 ZHIPU_API_KEY，使用 SimpleLLM（规则-based）")
        print("💡 如需使用智谱 AI，请设置环境变量: $env:ZHIPU_API_KEY='your-key'")
        llm_type = "simple"
    
    agent = MedicalAgent(llm_type=llm_type)
    
    while True:
        try:
            user_input = input("\n🧑 患者: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\n再见！祝您健康！")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                print("\n✅ 对话已重置")
                continue
            
            if user_input.lower() == 'info':
                print("\n📋 患者信息:")
                print(agent.patient_info)
                continue
            
            # 执行 Agent
            print("\n🤖 医生: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


def run_api():
    """启动 API 服务"""
    from api.agent_api import app
    print("启动 API 服务...")
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='医疗问诊 Agent')
    parser.add_argument('--mode', choices=['interactive', 'api'], 
                       default='interactive',
                       help='运行模式: interactive (交互式) 或 api (API服务)')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        run_api()
    else:
        run_interactive()
