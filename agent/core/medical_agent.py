"""
Medical Agent Core - ReAct 架构实现

ReAct = Reasoning + Acting
循环: Observation -> Thought -> Action -> Observation ...
"""

from typing import Dict, List, Optional, Any
import json
import re
import os
from datetime import datetime

# ============================================================
# LLM 客户端导入
# ============================================================

# 智谱 AI 客户端
try:
    from zhipuai import ZhipuAI
    ZHIPU_AVAILABLE = True
except ImportError:
    ZHIPU_AVAILABLE = False

# OpenAI 客户端（可选）
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================
# 本地 GPT-2 模型导入（已注释，保留备用）
# ============================================================
# from transformers import GPT2LMHeadModel, BertTokenizerFast
# import torch

# class LocalLLM:
#     """本地 GPT-2 模型封装（备用）"""
#     def __init__(self, model_path='save_model/model2'):
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.model = GPT2LMHeadModel.from_pretrained(model_path)
#         self.model = self.model.to(self.device)
#         self.model.eval()
#         
#         self.tokenizer = BertTokenizerFast(
#             'data/vocab/vocab.txt',
#             sep_token="[SEP]",
#             pad_token="[PAD]",
#             cls_token="[CLS]"
#         )
#         self.max_length = 100
#     
#     def generate(self, prompt: str) -> str:
#         """生成回复"""
#         text_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
#         input_ids = [self.tokenizer.cls_token_id] + text_ids + [self.tokenizer.sep_token_id]
#         input_ids = torch.tensor(input_ids).unsqueeze(0).to(self.device)
#         
#         response = []
#         for _ in range(self.max_length):
#             outputs = self.model(input_ids=input_ids)
#             next_token_logits = outputs.logits[0, -1, :]
#             next_token_probs = torch.softmax(next_token_logits, dim=-1)
#             next_token_id = torch.multinomial(next_token_probs, num_samples=1)
#             
#             if next_token_id.item() == self.tokenizer.sep_token_id:
#                 break
#             
#             response.append(next_token_id.item())
#             input_ids = torch.cat([input_ids, next_token_id.unsqueeze(0)], dim=-1)
#         
#         response_text = self.tokenizer.convert_ids_to_tokens(response)
#         return ''.join(response_text)


class ZhipuLLM:
    """智谱 AI LLM 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4-flash"):
        """
        初始化智谱 AI 客户端
        
        Args:
            api_key: 智谱 API Key，默认从环境变量 ZHIPU_API_KEY 读取
            model: 模型名称，默认 glm-4-flash（免费）
        """
        if not ZHIPU_AVAILABLE:
            raise ImportError("请先安装 zhipuai: pip install zhipuai")
        
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("请提供 api_key 或设置环境变量 ZHIPU_API_KEY")
        
        self.model = model
        self.client = ZhipuAI(api_key=self.api_key)
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        调用智谱 AI 生成回复
        
        Args:
            prompt: 输入提示
            temperature: 温度参数
            
        Returns:
            生成的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的医疗问诊助手，请简洁地回答。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"智谱 API 调用失败: {e}")
            return "我需要更多信息来帮助您。"


class SimpleLLM:
    """简化版 LLM（用于演示，实际可替换为 GPT-2 或 API）"""
    
    def generate(self, prompt: str) -> str:
        """
        基于规则的模拟生成
        实际使用时替换为:
        - 本地 GPT-2: 取消上面 LocalLLM 的注释
        - 或调用 ZhipuLLM / OpenAI API
        """
        # 解析 prompt 中的关键信息
        if "Thought:" in prompt:
            # 提取最后的问题
            lines = prompt.strip().split('\n')
            last_observation = ""
            for line in reversed(lines):
                if line.startswith("Observation:"):
                    last_observation = line.replace("Observation:", "").strip()
                    break
            
            # 模拟 Thought 生成
            if "头疼" in last_observation or "头痛" in last_observation:
                return "用户提到头疼症状，我需要询问更多细节：疼痛位置、持续时间、伴随症状。"
            elif "发烧" in last_observation:
                return "用户有发烧症状，需要询问体温、持续时间、是否有其他症状。"
            elif "肚子" in last_observation or "腹痛" in last_observation:
                return "用户有腹部不适，需要询问疼痛位置、性质、持续时间。"
            elif "感冒" in last_observation:
                return "用户提到感冒，需要询问具体症状：发烧、咳嗽、流鼻涕、喉咙痛等。"
            else:
                return "我需要进一步了解用户的症状细节，以便给出更准确的建议。"
        
        elif "Action:" in prompt:
            # 提取 Thought 内容
            thought_match = re.search(r'你的思考: (.+?)(?:\n|$)', prompt)
            thought = thought_match.group(1) if thought_match else ""
            
            # 根据 Thought 生成 Action
            if "感冒" in thought:
                return "ask_user[请问您感冒有哪些症状？比如发烧、咳嗽、流鼻涕、喉咙痛等？]"
            elif "头疼" in thought or "头痛" in thought:
                return "ask_user[请问您能描述一下头疼的具体位置吗？是前额、两侧还是后脑勺？]"
            elif "发烧" in thought:
                return "ask_user[请问您体温多少度？发烧持续多久了？]"
            elif "肚子" in thought or "腹痛" in thought:
                return "ask_user[请问腹痛的具体位置是哪里？是隐痛还是剧痛？]"
            elif "建议" in prompt or "推荐" in prompt:
                return "give_advice[建议您多休息，保持充足睡眠。如果症状持续，请及时就医。]"
            elif "查询" in prompt:
                return "search_knowledge[症状可能原因]"
            else:
                return "ask_user[能再详细描述一下您的症状吗？]"
        
        return "我需要更多信息来帮助您。"


class SimpleLLM:
    """简化版 LLM（用于演示，实际可替换为 GPT-2 或 API）"""
    
    def generate(self, prompt: str) -> str:
        """
        基于规则的模拟生成
        实际使用时替换为:
        - 本地 GPT-2: 取消上面 LocalLLM 的注释
        - 或调用 OpenAI/智谱 API
        """
        # 解析 prompt 中的关键信息
        if "Thought:" in prompt:
            # 提取最后的问题
            lines = prompt.strip().split('\n')
            last_observation = ""
            for line in reversed(lines):
                if line.startswith("Observation:"):
                    last_observation = line.replace("Observation:", "").strip()
                    break
            
            # 模拟 Thought 生成
            if "头疼" in last_observation or "头痛" in last_observation:
                return "用户提到头疼症状，我需要询问更多细节：疼痛位置、持续时间、伴随症状。"
            elif "发烧" in last_observation:
                return "用户有发烧症状，需要询问体温、持续时间、是否有其他症状。"
            elif "肚子" in last_observation or "腹痛" in last_observation:
                return "用户有腹部不适，需要询问疼痛位置、性质、持续时间。"
            else:
                return "我需要进一步了解用户的症状细节，以便给出更准确的建议。"
        
        elif "Action:" in prompt:
            # 模拟 Action 生成
            if "询问" in prompt or "了解" in prompt:
                return "ask_user[请问您能描述一下疼痛的具体位置吗？是前额、两侧还是后脑勺？]"
            elif "建议" in prompt or "推荐" in prompt:
                return "give_advice[建议您多休息，保持充足睡眠。如果症状持续，请及时就医。]"
            elif "查询" in prompt:
                return "search_knowledge[头疼可能原因]"
            else:
                return "ask_user[能再详细描述一下您的症状吗？]"
        
        return "我需要更多信息来帮助您。"


class MedicalAgent:
    """
    医疗问诊 Agent - ReAct 架构
    
    核心循环:
    1. Observation: 接收用户输入
    2. Thought: LLM 推理当前情况
    3. Action: 决定下一步动作（询问/建议/查询）
    4. 执行 Action，产生新的 Observation
    
    支持持久化存储：对话历史和患者信息自动保存到数据库
    """
    
    def __init__(self, session_id: str = None, max_iterations: int = 5, llm_type: str = "simple"):
        """
        初始化 Agent
        
        Args:
            session_id: 会话ID（用于持久化）
            max_iterations: 最大 ReAct 循环次数
            llm_type: LLM 类型，可选 "simple", "zhipu", "local"
        """
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.max_iterations = max_iterations
        self.memory: List[Dict[str, str]] = []  # 对话历史
        self.patient_info: Dict[str, Any] = {}  # 患者信息槽位
        
        # 初始化数据库
        try:
            from ..memory.session_db import get_db
            self.db = get_db()
            self._load_from_db()
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")
            self.db = None
        
        # 初始化 LLM
        if llm_type == "zhipu":
            try:
                self.llm = ZhipuLLM()
                print("✅ 已接入智谱 AI")
            except Exception as e:
                print(f"⚠️ 智谱 AI 初始化失败: {e}")
                print("🔄 回退到 SimpleLLM")
                self.llm = SimpleLLM()
        elif llm_type == "local":
            # self.llm = LocalLLM()  # 使用本地 GPT-2 时取消注释
            print("⚠️ 本地模型未启用，使用 SimpleLLM")
            self.llm = SimpleLLM()
        else:
            self.llm = SimpleLLM()
        
        # 工具注册
        self.tools = {
            "ask_user": self._tool_ask_user,
            "give_advice": self._tool_give_advice,
            "search_knowledge": self._tool_search_knowledge,
            "record_symptom": self._tool_record_symptom,
        }
    
    def _load_from_db(self):
        """从数据库加载会话数据"""
        if not self.db:
            return
        
        session_data = self.db.load_session(self.session_id)
        if session_data:
            self.patient_info = session_data.get('patient_info', {})
            self.memory = session_data.get('messages', [])
            print(f"📂 已加载历史会话: {self.session_id} ({len(self.memory)} 条消息)")
    
    def _save_to_db(self):
        """保存会话数据到数据库"""
        if not self.db:
            return
        
        self.db.save_session(self.session_id, self.patient_info, self.memory)
    
    def chat(self, user_input: str) -> str:
        """
        主入口：处理用户输入，返回 Agent 回复
        
        Args:
            user_input: 用户输入的症状描述
            
        Returns:
            Agent 的回复
        """
        # 记录用户输入
        self.memory.append({"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()})
        
        # 更新患者信息（简单关键词提取）
        self._extract_patient_info(user_input)
        
        # 检查是否已收集足够信息
        if self._has_enough_info():
            # 直接给出总结建议
            advice = self._generate_final_advice()
            self.memory.append({"role": "assistant", "content": advice})
            return advice
        
        # ReAct 循环
        for iteration in range(self.max_iterations):
            # Step 1: Thought - 推理当前情况
            thought = self._generate_thought()
            
            # Step 2: Action - 决定下一步动作
            action_str = self._generate_action(thought)
            action_name, action_input = self._parse_action(action_str)
            
            # Step 3: 执行 Action
            if action_name in self.tools:
                result = self.tools[action_name](action_input)
                
                # 如果是 ask_user 或 give_advice，直接返回给用户
                if action_name in ["ask_user", "give_advice"]:
                    self.memory.append({"role": "assistant", "content": result, "timestamp": datetime.now().isoformat()})
                    # 保存到数据库
                    self._save_to_db()
                    return result
                
                # 否则继续循环（如 search_knowledge, record_symptom）
                self.memory.append({
                    "role": "system",
                    "content": f"Action: {action_name}[{action_input}]\nResult: {result}"
                })
            else:
                # 未知动作，直接返回建议
                return "我理解您的症状了。建议您注意休息，如果症状持续或加重，请及时就医。"
        
        # 达到最大迭代次数，给出总结建议
        advice = self._generate_final_advice()
        self.memory.append({"role": "assistant", "content": advice})
        return advice
    
    def _has_enough_info(self) -> bool:
        """检查是否已收集足够信息"""
        # 获取已收集的信息
        symptom = self.patient_info.get("症状")
        duration = self.patient_info.get("持续时间")
        location = self.patient_info.get("疼痛位置")
        nature = self.patient_info.get("疼痛性质")
        
        # 对话轮数
        user_turns = len([m for m in self.memory if m["role"] == "user"])
        
        # 必须满足：有症状 + 持续时间 + (位置或性质)，才认为信息足够
        has_basic_info = symptom and duration
        has_detail_info = location or nature
        
        # 信息完整，可以给出建议
        if has_basic_info and has_detail_info:
            return True
        
        # 对话超过 5 轮，强制给出建议（避免无限追问）
        if user_turns >= 5:
            return True
        
        return False
    
    def _generate_thought(self) -> str:
        """生成 Thought：分析当前情况"""
        prompt = self._build_react_prompt("thought")
        return self.llm.generate(prompt)
    
    def _generate_action(self, thought: str) -> str:
        """生成 Action：决定下一步"""
        prompt = self._build_react_prompt("action", thought)
        return self.llm.generate(prompt)
    
    def _build_react_prompt(self, step: str, thought: str = "") -> str:
        """构建 ReAct 格式的 Prompt"""
        
        # 构建对话历史上下文
        context = ""
        for msg in self.memory[-5:]:  # 最近 5 轮
            if msg["role"] == "user":
                context += f"患者: {msg['content']}\n"
            elif msg["role"] == "assistant":
                context += f"医生: {msg['content']}\n"
        
        # 患者信息
        patient_summary = ""
        if self.patient_info:
            patient_summary = "已知信息:\n"
            for key, value in self.patient_info.items():
                patient_summary += f"- {key}: {value}\n"
        
        if step == "thought":
            return f"""你是一位专业的医疗问诊助手。请分析患者的症状，决定下一步如何帮助患者。

{patient_summary}
对话历史:
{context}

请分析当前情况，给出你的思考过程（简洁，一句话）。
Thought:"""
        
        else:  # action
            # 计算已收集的信息量
            user_turns = len([m for m in self.memory if m["role"] == "user"])
            has_duration = bool(self.patient_info.get("持续时间"))
            has_nature = bool(self.patient_info.get("疼痛性质"))
            has_location = bool(self.patient_info.get("疼痛位置"))
            
            # 判断是否应该给出建议
            should_advice = user_turns >= 3 and has_duration and (has_nature or has_location)
            
            advice_hint = ""
            if should_advice:
                advice_hint = """
**注意：您已经收集了足够的信息（症状、持续时间、性质/位置），应该给出建议而不是继续提问。**
**请使用 give_advice 动作给出综合建议。**"""
            
            return f"""基于以下思考，决定下一步动作:

{patient_summary}
对话历史:
{context}

你的思考: {thought}

**重要：你必须严格按照以下格式输出动作：**
- ask_user[你要问患者的问题] - 用于收集更多信息
- give_advice[你给患者的建议] - 当信息足够时给出建议
- search_knowledge[要查询的内容] - 查询医学知识
- record_symptom[要记录的症状] - 记录症状
{advice_hint}

**示例：**
- 信息不足时: ask_user[请问头疼的位置是哪里？]
- 信息足够时: give_advice[根据您的描述，您可能是...建议...]

**现在请输出你的动作（必须包含方括号）:**
Action:"""
    
    def _parse_action(self, action_str: str) -> tuple:
        """解析动作字符串"""
        # 清理可能的格式问题
        action_str = action_str.strip()
        
        # 智谱 AI 可能返回列表格式，提取第一个有效的 action
        lines = action_str.split('\n')
        for line in lines:
            line = line.strip()
            # 跳过列表标记
            if line.startswith('- ') or line.startswith('* '):
                line = line[2:]
            line = line.strip()
            
            # 尝试匹配 action_name[content] 格式
            match = re.match(r'(\w+)\[(.*)\]', line)
            if match:
                action_name = match.group(1)
                action_content = match.group(2)
                # 只返回第一个 ask_user 或 give_advice（直接给用户的）
                if action_name in ["ask_user", "give_advice"]:
                    return action_name, action_content
        
        # 如果没找到，再试一次找任何 action
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                line = line[2:]
            line = line.strip()
            
            match = re.match(r'(\w+)\[(.*)\]', line)
            if match:
                return match.group(1), match.group(2)
        
        # 如果都不匹配，直接使用内容作为 ask_user
        return "ask_user", action_str[:200]  # 限制长度
    
    def _extract_patient_info(self, text: str):
        """从文本中提取患者信息"""
        import re
        
        # 症状提取（医疗）
        if "头疼" in text or "头痛" in text:
            self.patient_info["症状"] = "头疼"
            self._add_symptom("头疼")
        if "发烧" in text or "发热" in text:
            self.patient_info["症状"] = "发烧"
            self._add_symptom("发烧")
        if "肚子" in text or "腹痛" in text or "胃疼" in text:
            self.patient_info["症状"] = "腹痛"
            self._add_symptom("腹痛")
        if "高血压" in text or "血压高" in text:
            self.patient_info["症状"] = "高血压"
            self._add_symptom("高血压")
        if "糖尿病" in text or "血糖" in text:
            self.patient_info["症状"] = "糖尿病"
            self._add_symptom("糖尿病")
        
        # 护理相关关键词
        nursing_keywords = [
            ("心衰", "心力衰竭"), ("心力衰竭", "心力衰竭"),
            ("心律失常", "心律失常"), ("房颤", "心房颤动"),
            ("冠心病", "冠心病"), ("心梗", "心肌梗死"),
            ("肺炎", "肺炎"), (" COPD", "慢性阻塞性肺病"),
            ("哮喘", "哮喘"), ("肺结核", "肺结核"),
            ("消化性溃疡", "消化性溃疡"), ("肝硬化", "肝硬化"),
            ("肾炎", "肾炎"), ("肾衰", "肾衰竭"),
            ("贫血", "贫血"), ("白血病", "白血病"),
            ("甲亢", "甲亢"), ("甲减", "甲减"),
            ("糖尿病", "糖尿病"), ("痛风", "痛风"),
            ("风湿", "风湿病"), ("类风湿", "类风湿关节炎"),
            ("骨折", "骨折"), ("外伤", "外伤"),
            ("烧伤", "烧伤"), ("烫伤", "烫伤"),
            ("手术", "手术"), ("术后", "术后"),
            ("化疗", "化疗"), ("放疗", "放疗"),
            ("护理", "护理"), ("护士", "护理"),
            ("输液", "输液"), ("打针", "注射"),
            ("换药", "换药"), ("换药", "伤口护理"),
        ]
        
        for keyword, condition in nursing_keywords:
            if keyword in text:
                self.patient_info["症状"] = condition
                self._add_symptom(condition)
                self.patient_info["科室"] = "护理"
                break
        if "咳嗽" in text:
            self._add_symptom("咳嗽")
        if "流鼻涕" in text or "鼻塞" in text:
            self._add_symptom("鼻塞/流涕")
        if "喉咙痛" in text or "咽痛" in text:
            self._add_symptom("喉咙痛")
        if "恶心" in text:
            self._add_symptom("恶心")
        if "呕吐" in text:
            self._add_symptom("呕吐")
        if "头晕" in text:
            self._add_symptom("头晕")
        
        # 持续时间提取（改进版，支持更多表述）
        # 天/日
        day_patterns = [
            r'(\d+)\s*[天日]',  # 3天、三日
            r'[三四五六七八九][天日]',  # 三天、五日（中文数字）
        ]
        for pattern in day_patterns:
            days = re.findall(pattern, text)
            if days:
                self.patient_info["持续时间"] = f"{days[0]}天"
                break
        
        # 小时
        if "小时" in text or "钟头" in text:
            hours = re.findall(r'(\d+)\s*小时?', text)
            if hours:
                self.patient_info["持续时间"] = f"{hours[0]}小时"
        
        # 周
        if "周" in text or "星期" in text:
            weeks = re.findall(r'(\d+)\s*[周星期]', text)
            if weeks:
                self.patient_info["持续时间"] = f"{weeks[0]}周"
        
        # 月
        if "月" in text:
            months = re.findall(r'(\d+)\s*月', text)
            if months:
                self.patient_info["持续时间"] = f"{months[0]}月"
        
        # 中文数字映射（简单版）
        chinese_nums = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', 
                       '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
        for cn, num in chinese_nums.items():
            if f'{cn}天' in text or f'{cn}日' in text:
                self.patient_info["持续时间"] = f"{num}天"
                break
        
        # 疼痛位置提取
        if "前额" in text or "额头" in text or "前面" in text:
            self.patient_info["疼痛位置"] = "前额"
        elif "后脑" in text or "后面" in text or "枕部" in text:
            self.patient_info["疼痛位置"] = "后脑勺"
        elif "两侧" in text or "太阳穴" in text:
            self.patient_info["疼痛位置"] = "两侧/太阳穴"
        
        # 疼痛性质提取
        if "跳痛" in text or "搏动" in text:
            self.patient_info["疼痛性质"] = "跳痛/搏动性疼痛"
        elif "刺痛" in text or "针扎" in text:
            self.patient_info["疼痛性质"] = "刺痛"
        elif "钝痛" in text or "胀痛" in text:
            self.patient_info["疼痛性质"] = "钝痛/胀痛"
        elif "持续" in text:
            self.patient_info["疼痛性质"] = "持续性疼痛"
        
        # 触发因素
        if "压力" in text or "紧张" in text or "累" in text:
            self.patient_info["可能诱因"] = "压力/疲劳"
        if "睡眠" in text or "熬夜" in text:
            self.patient_info["可能诱因"] = "睡眠不足"
    
    def _add_symptom(self, symptom: str):
        """添加症状到列表"""
        if "症状列表" not in self.patient_info:
            self.patient_info["症状列表"] = []
        if symptom not in self.patient_info["症状列表"]:
            self.patient_info["症状列表"].append(symptom)
    
    def _generate_final_advice(self) -> str:
        """生成最终建议（基于知识库）"""
        symptoms = self.patient_info.get("症状", "未知症状")
        duration = self.patient_info.get("持续时间", "未知")
        location = self.patient_info.get("疼痛位置", "")
        nature = self.patient_info.get("疼痛性质", "")
        trigger = self.patient_info.get("可能诱因", "")
        symptom_list = self.patient_info.get("症状列表", [])

        # 构建症状描述
        symptom_desc = symptoms
        if location:
            symptom_desc += f"（{location}）"
        if nature:
            symptom_desc += f"，性质为{nature}"

        # 症状总结
        summary = f"根据我们的对话，您的主要症状是：{symptom_desc}，持续时间{duration}。"
        if symptom_list:
            summary += f"\n伴随症状：{', '.join(symptom_list)}。"
        if trigger:
            summary += f"\n可能诱因：{trigger}。"

        # 查询知识库获取专业建议
        kb_advice = ""
        try:
            import os
            import sys
            # 确保工作目录正确
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, '..', '..')
            if os.path.exists(os.path.join(project_root, 'data')):
                os.chdir(project_root)
            
            from ..tools.knowledge_base import get_knowledge_base
            kb = get_knowledge_base()

            # 构建查询
            query = f"{symptoms}"
            results = kb.search(query, top_k=2)

            if results:
                kb_advice = "\n\n根据医学知识库的相关信息：\n"
                for i, item in enumerate(results, 1):
                    kb_advice += f"\n【参考{i}】{item['department']}\n"
                    kb_advice += f"类似问题：{item['question'][:60]}...\n"
                    kb_advice += f"专业建议：{item['answer'][:150]}...\n"
        except Exception as e:
            print(f"知识库查询失败: {e}")

        # 通用自我护理建议
        care_advice = """

通用自我护理建议：
1. 保证充足休息，避免过度劳累
2. 保持规律作息，避免熬夜
3. 多喝水，保持身体水分
4. 适当放松，减轻压力"""

        if symptoms == "头疼":
            care_advice += "\n5. 可在安静、光线柔和的环境中休息"
            care_advice += "\n6. 适当按摩太阳穴或颈部"

        # 就医建议
        medical_advice = """

建议就医的情况：
- 症状持续加重或超过一周不缓解
- 出现剧烈疼痛、意识模糊、呼吸困难
- 伴有高烧（超过39°C）或持续低烧
- 出现新的严重症状

以上信息仅供参考，不能替代专业医生的诊断。如症状持续，请及时就医。"""

        return summary + kb_advice + care_advice + medical_advice
    
    # ==================== 工具函数 ====================
    
    def _tool_ask_user(self, question: str) -> str:
        """向用户提问"""
        return question
    
    def _tool_give_advice(self, advice: str) -> str:
        """给出建议"""
        return f"{advice}\n\n（以上建议仅供参考，不能替代专业医生的诊断）"
    
    def _tool_search_knowledge(self, query: str) -> str:
        """查询知识库（已接入真实医学数据）"""
        try:
            from ..tools.knowledge_base import get_knowledge_base
            kb = get_knowledge_base()
            return kb.get_answer(query)
        except Exception as e:
            return f"知识库查询失败: {e}。建议咨询专业医生。"
    
    def _tool_record_symptom(self, symptom: str) -> str:
        """记录症状"""
        if "症状" not in self.patient_info:
            self.patient_info["症状列表"] = []
        self.patient_info["症状列表"].append(symptom)
        return f"已记录症状: {symptom}"
    
    def reset(self):
        """重置对话状态"""
        self.memory = []
        self.patient_info = {}


if __name__ == "__main__":
    # 测试 Agent
    agent = MedicalAgent()
    
    print("=" * 50)
    print("医疗问诊 Agent - 测试模式")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        user_input = input("\n患者: ")
        if user_input.lower() == "exit":
            break
        
        response = agent.chat(user_input)
        print(f"\n医生: {response}")
