# AI Medical Agent

基于 ReAct 架构的智能医疗问诊 Agent，实现推理-行动循环的多轮对话系统。

## 核心特性

- 🧠 **ReAct 架构** - 推理(Reasoning) + 行动(Acting) 循环
- 💬 **多轮对话** - 智能追问，逐步收集症状信息
- 🏥 **医学知识库** - 基于 80万+ 真实医疗问答数据
- 🔧 **工具调用** - 模块化工具设计，支持扩展
- 💾 **会话管理** - SQLite 持久化，支持历史记录
- 🌐 **Web 界面** - React 风格前端，实时对话

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask + Python 3.10+ |
| LLM | 智谱 GLM-4-Flash (默认) / GPT-2 (本地) |
| 架构 | ReAct (Reasoning + Acting) |
| 数据库 | SQLite (会话存储) |
| 前端 | HTML5 + CSS3 + JavaScript |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/caoxuning/ai-medical-agent.git
cd ai-medical-agent
```

### 2. 安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 设置环境变量
set ZHIPU_API_KEY=your_api_key_here  # Windows
export ZHIPU_API_KEY=your_api_key_here  # Linux/Mac
```

获取 API Key: https://open.bigmodel.cn/

### 4. 启动服务

**方式一：交互式运行**
```bash
python run_agent.py
```

**方式二：API 服务**
```bash
python run_agent.py --mode api
# 或
python api/agent_api.py
```

**方式三：Web 界面**
```bash
python api/agent_api.py
# 访问 http://localhost:5000
```

## 项目结构

```
ai-medical-agent/
├── agent/                      # Agent 核心
│   ├── core/
│   │   └── medical_agent.py    # ReAct Agent 主类
│   ├── memory/
│   │   ├── conversation_memory.py  # 对话记忆
│   │   └── session_db.py       # SQLite 会话存储
│   ├── tools/
│   │   ├── medical_tools.py    # 工具集合
│   │   └── knowledge_base.py   # 医学知识库
│   └── prompts/
│       └── react_prompts.py    # Prompt 模板
├── api/
│   └── agent_api.py            # Flask API 服务
├── frontend/
│   └── index.html              # Web 界面
├── data/                       # 数据文件
│   └── medical_knowledge/      # 医学知识库
├── run_agent.py                # 启动脚本
├── requirements.txt
└── README.md
```

## API 接口

### 对话接口

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_001",
    "message": "我最近头疼，已经持续三天了"
  }'
```

**响应：**
```json
{
  "response": "请问您能描述一下疼痛的具体位置吗？",
  "session_id": "user_001",
  "patient_info": {
    "症状": "头疼",
    "持续时间": "3天"
  }
}
```

### 获取历史记录

```bash
curl http://localhost:5000/api/history?session_id=user_001
```

### 重置会话

```bash
curl -X POST http://localhost:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user_001"}'
```

## ReAct 循环流程

```
患者输入: "我最近头疼，已经持续三天了"
    ↓
Observation: 用户提到头疼症状，持续时间3天
    ↓
Thought: 需要询问更多细节：疼痛位置、伴随症状
    ↓
Action: ask_user[请问您能描述一下疼痛的具体位置吗？]
    ↓
执行 Action → 返回给患者
```

## 工具列表

| 工具 | 功能 |
|------|------|
| `ask_user` | 向患者询问更多信息 |
| `give_advice` | 基于当前信息给出建议 |
| `search_knowledge` | 查询医学知识库 |
| `record_symptom` | 记录症状信息 |

## 知识库数据

- **数据来源**: Chinese Medical Dialogue Dataset
- **数据规模**: 80万+ 真实医患对话
- **科室覆盖**: 内科、外科、妇产科、儿科、肿瘤科、男科

## 本地模型支持

如需使用本地 GPT-2 模型（已训练）：

1. 编辑 `agent/core/medical_agent.py`
2. 取消 `LocalLLM` 类注释
3. 修改初始化：`self.llm = LocalLLM()`

模型路径: `save_model/model2/`

## 开发计划

- [ ] 症状实体识别 (NER)
- [ ] 知识图谱接入
- [ ] 多模态支持 (图片上传)
- [ ] 语音对话
- [ ] 部署文档

## 免责声明

本系统仅供学习和研究使用，提供的医疗建议**不能替代专业医生的诊断和治疗**。如有健康问题，请及时就医。

## License

MIT License
