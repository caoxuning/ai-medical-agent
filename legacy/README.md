# 原 GPT-2 医疗对话项目代码备份

此目录包含原项目的代码备份，已注释/停用。

## 文件说明

| 文件 | 原功能 | 状态 |
|-----|-------|------|
| `FlaskAPI.py.bak` | Flask API 服务 | 已迁移至 `api/agent_api.py` |
| `模型应用.py.bak` | 命令行交互 | 已迁移至 `run_agent.py` |
| `train.py.bak` | GPT-2 模型训练 | 保留备用 |
| `dataset.py.bak` | 数据集定义 | 保留备用 |
| `dataloader.py.bak` | 数据加载器 | 保留备用 |
| `preprocess.py.bak` | 数据预处理 | 保留备用 |
| `config.py.bak` | 配置文件 | 保留备用 |
| `ptest.py.bak` | 测试脚本 | 保留备用 |

## 模型文件

本地 GPT-2 模型文件保留在原位置：
- `../save_model/model2/` - 训练好的模型
- `../data/vocab/vocab.txt` - 词表文件
- `../data/processed/` - 处理后的数据

## 如需使用本地模型

编辑 `../agent/core/medical_agent.py`：

1. 取消 `LocalLLM` 类的注释
2. 将 `self.llm = SimpleLLM()` 替换为 `self.llm = LocalLLM()`

## 原项目架构

```
原架构: GPT-2 生成模型
        ↓
    输入症状描述
        ↓
    模型生成回复
        ↓
    返回给患者

新架构: ReAct Agent
        ↓
    Observation (观察)
        ↓
    Thought (推理)
        ↓
    Action (行动)
        ↓
    执行工具/生成回复
        ↓
    返回给患者
```
