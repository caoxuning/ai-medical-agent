"""
Agent API 服务
基于 Flask 的医疗 Agent 接口
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.core.medical_agent import MedicalAgent

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # 允许跨域请求

# 存储会话（生产环境应使用 Redis 等）
sessions: dict = {}


def get_or_create_agent(session_id: str) -> MedicalAgent:
    """获取或创建 Agent 实例（支持持久化）"""
    if session_id not in sessions:
        # 传入 session_id 以支持持久化
        sessions[session_id] = MedicalAgent(session_id=session_id, llm_type="zhipu")
    return sessions[session_id]


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    对话接口
    
    Request:
        {
            "session_id": "用户会话ID",
            "message": "用户输入"
        }
    
    Response:
        {
            "response": "Agent回复",
            "session_id": "会话ID",
            "thought": "推理过程（调试用）"
        }
    """
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "请提供输入消息"}), 400
        
        # 获取 Agent 实例
        agent = get_or_create_agent(session_id)
        
        # 执行 ReAct 循环
        response = agent.chat(message)
        
        return jsonify({
            "response": response,
            "session_id": session_id,
            "patient_info": agent.patient_info
        })
        
    except Exception as e:
        print(f"处理请求时出错: {e}")
        return jsonify({"error": "处理请求时出错"}), 500


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """
    重置会话
    
    Request:
        {"session_id": "用户会话ID"}
    """
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in sessions:
            sessions[session_id].reset()
            del sessions[session_id]
        
        return jsonify({"message": "会话已重置", "session_id": session_id})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取对话历史"""
    session_id = request.args.get('session_id', 'default')
    
    if session_id not in sessions:
        return jsonify({"history": []})
    
    agent = sessions[session_id]
    return jsonify({
        "history": agent.memory,
        "patient_info": agent.patient_info
    })


@app.route('/api/tools', methods=['GET'])
def list_tools():
    """列出可用工具"""
    tools = {
        "ask_user": "向患者询问更多信息",
        "give_advice": "给出医疗建议",
        "search_knowledge": "查询医学知识库",
        "record_symptom": "记录症状信息"
    }
    return jsonify({"tools": tools})


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """列出所有会话"""
    try:
        from agent.memory.session_db import get_db
        db = get_db()
        sessions_list = db.list_sessions(limit=50)
        stats = db.get_stats()
        return jsonify({
            "sessions": sessions_list,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话详情"""
    try:
        from agent.memory.session_db import get_db
        db = get_db()
        session_data = db.load_session(session_id)
        if session_data:
            return jsonify(session_data)
        return jsonify({"error": "会话不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    try:
        from agent.memory.session_db import get_db
        db = get_db()
        db.delete_session(session_id)
        # 从内存中也删除
        if session_id in sessions:
            del sessions[session_id]
        return jsonify({"message": "会话已删除"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "service": "medical-agent-api"})


@app.route('/')
def index():
    """首页 - 返回前端页面"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """提供静态文件"""
    return send_from_directory('../frontend', path)


if __name__ == '__main__':
    print("=" * 50)
    print("医疗问诊 Agent API 服务")
    print("=" * 50)
    print("接口地址: http://localhost:5000")
    print("文档: http://localhost:5000/")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
