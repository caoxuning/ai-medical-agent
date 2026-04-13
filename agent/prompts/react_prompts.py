"""
Prompt 模板管理
定义 ReAct Agent 的各种 Prompt 模板
"""


class ReActPrompts:
    """
    ReAct 架构的 Prompt 模板
    
    ReAct = Reasoning (推理) + Acting (行动)
    """
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一位专业的医疗问诊助手，基于 ReAct 架构帮助患者了解症状。

你的任务是通过多轮对话收集患者信息，给出初步建议，并在必要时建议就医。

重要原则：
1. 保持专业、友善的语气
2. 逐步收集症状信息，不要一次性问太多问题
3. 基于已有信息给出合理建议
4. 明确告知用户建议仅供参考，不能替代医生诊断
5. 遇到紧急情况（胸痛、呼吸困难、意识模糊等），立即建议就医

你可以使用以下工具：
{tool_descriptions}
"""
    
    # Thought 生成模板
    THOUGHT_TEMPLATE = """请分析以下患者情况，给出你的思考过程。

{patient_summary}
对话历史:
{conversation_history}

请思考：
1. 患者当前主要症状是什么？
2. 还需要了解哪些信息？
3. 下一步应该采取什么行动？

Thought:"""
    
    # Action 生成模板
    ACTION_TEMPLATE = """基于你的思考，选择下一步动作。

你的思考: {thought}

可用动作:
1. ask_user[问题] - 向患者询问更多信息
2. give_advice[建议] - 基于当前信息给出建议
3. search_knowledge[查询内容] - 查询医学知识库
4. record_symptom[症状] - 记录症状信息

请以 "动作名[参数]" 的格式输出。

Action:"""
    
    # 最终建议模板
    FINAL_ADVICE_TEMPLATE = """基于以下患者信息，给出综合建议：

{patient_summary}
对话历史:
{conversation_history}

请给出：
1. 症状总结
2. 可能的原因（非诊断）
3. 自我护理建议
4. 何时需要就医

建议:"""
    
    # 紧急情况提示
    EMERGENCY_PROMPT = """患者描述可能涉及紧急医疗情况。

请立即：
1. 告知患者这可能需要紧急医疗关注
2. 建议立即拨打急救电话或前往急诊
3. 保持冷静，不要给出具体治疗建议

紧急建议:"""


class SlotFillingPrompts:
    """
    槽位填充相关的 Prompt 模板
    """
    
    # 症状提取
    SYMPTOM_EXTRACTION = """从以下描述中提取症状信息：

描述: {text}

请以 JSON 格式输出：
{{
    "症状": "主要症状",
    "部位": "身体部位",
    "持续时间": "持续时间",
    "严重程度": "轻微/中等/严重"
}}"""
    
    # 追问生成
    FOLLOW_UP_QUESTION = """基于以下患者信息，生成一个追问问题：

已知信息:
{known_info}

缺失信息:
{missing_info}

请生成一个自然、友善的问题来询问缺失的信息：
问题:"""


# 便捷函数
def get_system_prompt(tool_descriptions: str) -> str:
    """获取系统提示词"""
    return ReActPrompts.SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)


def get_thought_prompt(patient_summary: str, conversation_history: str) -> str:
    """获取 Thought 提示词"""
    return ReActPrompts.THOUGHT_TEMPLATE.format(
        patient_summary=patient_summary,
        conversation_history=conversation_history
    )


def get_action_prompt(thought: str) -> str:
    """获取 Action 提示词"""
    return ReActPrompts.ACTION_TEMPLATE.format(thought=thought)
