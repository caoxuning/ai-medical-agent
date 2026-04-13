"""
专门处理护理考试资料 PDF
提取考点知识点
"""
import pdfplumber
import re
import json
import os

def extract_nursing_knowledge(pdf_path, source_name):
    """提取护理知识点"""
    knowledge_list = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            current_topic = ""
            current_content = ""
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 5:
                    continue
                
                # 跳过广告/页眉
                if '陶老师' in line and len(line) < 50:
                    continue
                if '应用商店' in line or '微信联系' in line:
                    continue
                if re.match(r'^\d+$', line):  # 纯数字页码
                    continue
                
                # 检测考点标题（通常包含数字和关键词）
                if re.match(r'^\d+[、\.\s]', line) or '考点' in line or '---' in line:
                    # 保存之前的内容
                    if current_topic and current_content:
                        knowledge_list.append({
                            'topic': current_topic,
                            'content': current_content[:500],
                            'source': source_name,
                            'page': page_num + 1
                        })
                    current_topic = line
                    current_content = ""
                else:
                    current_content += line + " "
            
            # 保存最后一个
            if current_topic and current_content:
                knowledge_list.append({
                    'topic': current_topic,
                    'content': current_content[:500],
                    'source': source_name,
                    'page': page_num + 1
                })
    
    return knowledge_list

def main():
    """处理所有护理 PDF"""
    nursing_dir = "data/nursing"
    all_knowledge = []
    
    pdf_files = [f for f in os.listdir(nursing_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(nursing_dir, pdf_file)
        print(f"📄 处理: {pdf_file}")
        
        try:
            knowledge = extract_nursing_knowledge(pdf_path, pdf_file)
            print(f"  ✅ 提取 {len(knowledge)} 个知识点")
            all_knowledge.extend(knowledge)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    print(f"\n📊 总计提取: {len(all_knowledge)} 个护理知识点")
    
    # 转换为知识库格式
    kb_entries = []
    for item in all_knowledge:
        kb_entries.append({
            'department': '护理',
            'title': item['topic'][:50],
            'question': item['topic'],
            'answer': item['content'],
            'text': f"【护理-{item['source'][:10]}】{item['topic'][:80]}\n{item['content'][:200]}",
            'source': item['source']
        })
    
    # 保存
    output_path = "data/medical_knowledge/nursing_knowledge.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kb_entries, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 护理知识库已保存: {output_path}")
    
    # 显示样本
    if kb_entries:
        print(f"\n📄 样本:")
        print(f"  标题: {kb_entries[0]['title']}")
        print(f"  内容: {kb_entries[0]['answer'][:100]}...")
    
    return kb_entries

if __name__ == "__main__":
    main()
