"""
批量处理本地 medical.txt 全部数据
"""
import json
import os

def process_all_local_data():
    """处理全部本地数据"""
    txt_path = "data/raw/medical.txt"
    
    if not os.path.exists(txt_path):
        print(f"❌ 文件不存在: {txt_path}")
        return []
    
    print("=" * 60)
    print("处理本地 medical.txt 全部数据")
    print("=" * 60)
    
    # 获取文件大小
    file_size = os.path.getsize(txt_path) / (1024 * 1024)
    print(f"📄 文件大小: {file_size:.1f} MB")
    
    # 读取并解析
    print("\n正在读取文件...")
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    print(f"📊 总行数: {len(lines)}")
    
    # 解析问答对
    print("\n正在解析问答对...")
    qa_pairs = []
    i = 0
    
    while i < len(lines) - 1:
        q = lines[i].strip()
        a = lines[i+1].strip() if i+1 < len(lines) else ""
        
        # 过滤条件
        if q and a and len(q) > 5 and len(a) > 5:
            qa_pairs.append({
                'department': '综合',
                'title': q[:50],
                'question': q,
                'answer': a,
                'text': f"【综合】{q[:80]}\n回答：{a[:200]}",
                'source': 'medical.txt'
            })
        
        i += 2
        
        # 显示进度
        if len(qa_pairs) % 10000 == 0:
            print(f"  已处理: {len(qa_pairs)} 条问答对...")
    
    print(f"\n✅ 解析完成: {len(qa_pairs)} 条问答对")
    
    return qa_pairs

def merge_with_existing(qa_pairs):
    """与现有知识库合并"""
    print("\n" + "=" * 60)
    print("合并知识库")
    print("=" * 60)
    
    # 加载现有知识库
    kb_path = "data/medical_knowledge/knowledge_base.json"
    with open(kb_path, 'r', encoding='utf-8') as f:
        existing_kb = json.load(f)
    
    print(f"📚 现有知识库: {len(existing_kb)} 条")
    print(f"📥 新增本地数据: {len(qa_pairs)} 条")
    
    # 合并
    merged_kb = existing_kb + qa_pairs
    
    print(f"📊 合并后总计: {len(merged_kb)} 条")
    
    # 保存
    print("\n正在保存...")
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(merged_kb, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(kb_path) / (1024 * 1024)
    print(f"✅ 保存完成: {kb_path}")
    print(f"📦 文件大小: {file_size:.1f} MB")
    
    return merged_kb

if __name__ == "__main__":
    qa_pairs = process_all_local_data()
    if qa_pairs:
        merge_with_existing(qa_pairs)
        
        print("\n" + "=" * 60)
        print("🎉 知识库更新完成!")
        print("=" * 60)
        print(f"现在知识库共有 {len(qa_pairs) + 3088} 条数据")
