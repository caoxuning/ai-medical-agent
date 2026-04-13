"""
处理全部开源医疗数据 - 79万条
"""
import os
import json
import csv

def process_all_open_source_data():
    """处理全部开源数据"""
    base_dir = "data/medical_knowledge/Chinese-medical-dialogue-data-master/Data_数据/"
    
    if not os.path.exists(base_dir):
        print(f"❌ 数据目录不存在: {base_dir}")
        return []
    
    print("=" * 70)
    print("处理全部开源医疗数据")
    print("=" * 70)
    
    # 科室列表
    departments = [
        ("Andriatria_男科", "男科"),
        ("IM_内科", "内科"),
        ("OAGD_妇产科", "妇产科"),
        ("Oncology_肿瘤科", "肿瘤科"),
        ("Pediatric_儿科", "儿科"),
        ("Surgical_外科", "外科"),
    ]
    
    all_knowledge = []
    
    for folder, dept_name in departments:
        dept_dir = os.path.join(base_dir, folder)
        
        if not os.path.exists(dept_dir):
            print(f"⚠️ 跳过 {dept_name}: 目录不存在")
            continue
        
        print(f"\n📂 处理 {dept_name}...")
        
        # 查找所有 CSV 文件
        csv_files = [f for f in os.listdir(dept_dir) if f.endswith('.csv')]
        
        dept_count = 0
        for csv_file in csv_files:
            csv_path = os.path.join(dept_dir, csv_file)
            
            try:
                # 使用 GBK 编码读取
                with open(csv_path, 'r', encoding='gbk', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        # 获取字段
                        title = row.get('title', '')
                        question = row.get('ask', '') or row.get('question', '')
                        answer = row.get('answer', '')
                        
                        if not answer or len(answer) < 10:
                            continue
                        
                        # 构建知识条目
                        knowledge_entry = {
                            'department': dept_name,
                            'title': title,
                            'question': question,
                            'answer': answer,
                            'text': f"【{dept_name}】{title[:50]}\n问题：{question[:100]}\n回答：{answer[:200]}",
                            'source': f'{folder}/{csv_file}'
                        }
                        
                        all_knowledge.append(knowledge_entry)
                        dept_count += 1
                        
                        # 显示进度
                        if dept_count % 20000 == 0:
                            print(f"  已处理: {dept_count} 条...")
                
                print(f"  ✅ {csv_file}: 累计 {dept_count} 条")
                
            except Exception as e:
                print(f"  ⚠️ 文件 {csv_file} 处理失败: {e}")
        
        print(f"  📊 {dept_name} 总计: {dept_count} 条")
    
    print(f"\n{'='*70}")
    print(f"📊 开源数据总计: {len(all_knowledge)} 条")
    print(f"{'='*70}")
    
    return all_knowledge

def save_full_knowledge_base(open_source_data):
    """保存完整知识库"""
    print("\n" + "=" * 70)
    print("合并所有数据")
    print("=" * 70)
    
    # 加载本地数据
    local_kb = []
    local_path = "data/raw/medical.txt"
    if os.path.exists(local_path):
        print("📄 处理本地 medical.txt...")
        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines) - 1:
            q = lines[i].strip()
            a = lines[i+1].strip() if i+1 < len(lines) else ""
            
            if q and a and len(q) > 5 and len(a) > 5:
                local_kb.append({
                    'department': '综合',
                    'title': q[:50],
                    'question': q,
                    'answer': a,
                    'text': f"【综合】{q[:80]}\n回答：{a[:200]}",
                    'source': 'medical.txt'
                })
            i += 2
        
        print(f"  ✅ 本地数据: {len(local_kb)} 条")
    
    # 加载护理数据
    nursing_kb = []
    nursing_path = "data/medical_knowledge/nursing_knowledge_cleaned.json"
    if os.path.exists(nursing_path):
        print("📄 加载护理数据...")
        with open(nursing_path, 'r', encoding='utf-8') as f:
            nursing_kb = json.load(f)
        print(f"  ✅ 护理数据: {len(nursing_kb)} 条")
    
    # 合并所有数据
    print("\n📊 合并统计:")
    print(f"  - 开源医疗数据: {len(open_source_data)} 条")
    print(f"  - 本地数据: {len(local_kb)} 条")
    print(f"  - 护理数据: {len(nursing_kb)} 条")
    
    merged_kb = open_source_data + local_kb + nursing_kb
    
    print(f"\n📦 合并后总计: {len(merged_kb)} 条")
    
    # 保存
    output_path = "data/medical_knowledge/knowledge_base_full.json"
    print(f"\n💾 正在保存到: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_kb, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ 保存完成!")
    print(f"📦 文件大小: {file_size:.1f} MB")
    
    # 同时更新主知识库
    import shutil
    shutil.copy(output_path, "data/medical_knowledge/knowledge_base.json")
    print(f"✅ 已更新主知识库")
    
    return merged_kb

if __name__ == "__main__":
    open_source_data = process_all_open_source_data()
    if open_source_data:
        save_full_knowledge_base(open_source_data)
        
        print("\n" + "=" * 70)
        print("🎉 完整知识库构建完成!")
        print("=" * 70)
