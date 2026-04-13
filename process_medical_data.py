"""
处理中文医疗对话数据集 - GBK编码版
"""
import os
import json
import csv

def process_medical_data():
    """处理医疗数据为知识库格式"""
    base_dir = "data/medical_knowledge/Chinese-medical-dialogue-data-master/Data_数据/"
    
    if not os.path.exists(base_dir):
        print(f"❌ 数据目录不存在: {base_dir}")
        return None
    
    print("正在处理医疗数据...\n")
    
    # 科室列表
    departments = [
        ("Andriatria_男科", "男科"),
        ("IM_内科", "内科"),
        ("OAGD_妇产科", "妇产科"),
        ("Oncology_肿瘤科", "肿瘤科"),
        ("Pediatric_儿科", "儿科"),
        ("Surgical_外科", "外科"),
    ]
    
    knowledge_base = []
    
    for folder, dept_name in departments:
        dept_dir = os.path.join(base_dir, folder)
        
        if not os.path.exists(dept_dir):
            print(f"⚠️ 跳过 {dept_name}: 目录不存在")
            continue
        
        print(f"📂 处理 {dept_name}...")
        
        # 查找 CSV 文件
        csv_files = [f for f in os.listdir(dept_dir) if f.endswith('.csv')]
        
        count = 0
        for csv_file in csv_files:
            csv_path = os.path.join(dept_dir, csv_file)
            
            try:
                # 使用 GBK 编码读取
                with open(csv_path, 'r', encoding='gbk', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    
                    for i, row in enumerate(reader):
                        if i >= 300:  # 每个文件取前 300 条
                            break
                        
                        # 获取字段
                        title = row.get('title', '')
                        question = row.get('ask', '') or row.get('question', '')
                        answer = row.get('answer', '')
                        
                        if not answer or len(answer) < 10:
                            continue
                        
                        # 构建知识条目
                        knowledge_entry = {
                            "department": dept_name,
                            "title": title,
                            "question": question,
                            "answer": answer[:300],  # 限制长度
                            "text": f"【{dept_name}】{title}\n问题：{question[:100]}\n回答：{answer[:200]}"
                        }
                        
                        knowledge_base.append(knowledge_entry)
                        count += 1
                        
            except Exception as e:
                print(f"  ⚠️ 文件 {csv_file} 处理失败: {e}")
        
        print(f"  ✅ {dept_name}: {count} 条记录")
    
    print(f"\n📊 总计处理: {len(knowledge_base)} 条记录")
    
    # 保存为 JSON
    output_file = "data/medical_knowledge/knowledge_base.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 知识库已保存: {output_file}")
    print(f"📦 文件大小: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # 显示样本
    if knowledge_base:
        print(f"\n📄 样本数据:")
        print(f"  科室: {knowledge_base[0]['department']}")
        print(f"  标题: {knowledge_base[0]['title']}")
        print(f"  问题: {knowledge_base[0]['question'][:50]}...")
    
    return knowledge_base

if __name__ == "__main__":
    process_medical_data()
