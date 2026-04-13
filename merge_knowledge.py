"""
提取护理知识文件内容并构建知识库
支持 PDF 和 Word 格式
"""
import os
import json
import re

def extract_pdf_text(pdf_path):
    """提取 PDF 文本（使用 pdfplumber 效果更好）"""
    text = ""
    
    # 先尝试 pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception as e:
        print(f"  ⚠️ pdfplumber 失败，尝试 pypdf: {e}")
    
    # 回退到 pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"  ⚠️ PDF 提取失败 {pdf_path}: {e}")
        return ""

def extract_docx_text(docx_path):
    """提取 Word 文本"""
    try:
        from docx import Document
        doc = Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"  ⚠️ Word 提取失败 {docx_path}: {e}")
        return ""

def parse_qa_pairs(text, source_name):
    """解析问答对"""
    qa_pairs = []
    
    # 按行分割
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    current_q = None
    current_a = None
    
    for line in lines:
        # 跳过页眉页脚、页码等
        if re.match(r'^\d+$', line):  # 纯数字（页码）
            continue
        if len(line) < 5:  # 太短跳过
            continue
        
        # 检测问题模式（数字开头、问号、关键词等）
        is_question = False
        
        # 模式1: 数字+点/顿号开头
        if re.match(r'^\d+[\.、]', line):
            is_question = True
        # 模式2: 包含问号
        elif '?' in line or '？' in line:
            is_question = True
        # 模式3: 括号数字开头
        elif re.match(r'^\(\d+\)', line):
            is_question = True
        
        if is_question:
            # 保存之前的问答对
            if current_q and current_a:
                qa_pairs.append({
                    'question': current_q,
                    'answer': current_a,
                    'source': source_name
                })
            # 开始新问题
            current_q = line
            current_a = ""
        else:
            # 继续答案
            if current_q:
                if current_a:
                    current_a += " " + line
                else:
                    current_a = line
    
    # 保存最后一对
    if current_q and current_a:
        qa_pairs.append({
            'question': current_q,
            'answer': current_a,
            'source': source_name
        })
    
    return qa_pairs

def extract_knowledge_chunks(text, source_name, chunk_size=300):
    """将文本切分为知识块（改进版，提取更多有效内容）"""
    chunks = []
    
    # 清理文本
    text = re.sub(r'\n+', '\n', text)  # 合并多个换行
    text = re.sub(r'\s+', ' ', text)   # 合并多个空格
    
    # 按行分割并过滤
    lines = text.split('\n')
    lines = [line.strip() for line in lines if len(line.strip()) > 10]
    
    # 合并相关行形成知识块
    current_chunk = ""
    for line in lines:
        # 跳过页眉页脚
        if re.match(r'^\d+$', line):  # 纯数字
            continue
        if '页' in line and len(line) < 10:  # 页码
            continue
        
        # 如果行以数字或特定标记开头，可能是新知识点
        if re.match(r'^\d+[\.、\s]', line) or re.match(r'^[\(（]\d+[\)）]', line):
            if current_chunk and len(current_chunk) > 20:
                chunks.append({
                    'text': current_chunk[:chunk_size],
                    'source': source_name
                })
            current_chunk = line
        else:
            current_chunk += " " + line
        
        # 限制单个块大小
        if len(current_chunk) > chunk_size:
            chunks.append({
                'text': current_chunk[:chunk_size],
                'source': source_name
            })
            current_chunk = ""
    
    # 添加最后一个块
    if current_chunk and len(current_chunk) > 20:
        chunks.append({
            'text': current_chunk[:chunk_size],
            'source': source_name
        })
    
    return chunks[:800]  # 限制总数

def process_nursing_files():
    """处理护理文件"""
    nursing_dir = "data/nursing"
    
    if not os.path.exists(nursing_dir):
        print(f"❌ 护理目录不存在: {nursing_dir}")
        return []
    
    all_knowledge = []
    
    files = os.listdir(nursing_dir)
    print(f"📂 发现 {len(files)} 个护理文件")
    
    for filename in files:
        filepath = os.path.join(nursing_dir, filename)
        print(f"\n📄 处理: {filename}")
        
        if filename.endswith('.pdf'):
            text = extract_pdf_text(filepath)
            # PDF 通常结构复杂，按知识块处理
            chunks = extract_knowledge_chunks(text, filename)
            for chunk in chunks:
                all_knowledge.append({
                    'department': '护理',
                    'title': chunk['text'][:50],
                    'question': chunk['text'][:100],
                    'answer': chunk['text'],
                    'text': f"【护理-{filename[:10]}】{chunk['text'][:150]}",
                    'source': filename
                })
            print(f"  ✅ 提取 {len(chunks)} 个知识块")
            
        elif filename.endswith('.docx'):
            text = extract_docx_text(filepath)
            # Word 尝试解析问答对
            qa_pairs = parse_qa_pairs(text, filename)
            if qa_pairs:
                for qa in qa_pairs[:200]:  # 限制数量
                    all_knowledge.append({
                        'department': '护理',
                        'title': qa['question'][:50],
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'text': f"【护理】{qa['question'][:80]}\n回答：{qa['answer'][:150]}",
                        'source': filename
                    })
                print(f"  ✅ 提取 {len(qa_pairs)} 个问答对")
            else:
                # 如果解析不出问答对，按知识块处理
                chunks = extract_knowledge_chunks(text, filename)
                for chunk in chunks:
                    all_knowledge.append({
                        'department': '护理',
                        'title': chunk['text'][:50],
                        'question': chunk['text'][:100],
                        'answer': chunk['text'],
                        'text': f"【护理-{filename[:10]}】{chunk['text'][:150]}",
                        'source': filename
                    })
                print(f"  ✅ 提取 {len(chunks)} 个知识块")
    
    print(f"\n📊 护理知识总计: {len(all_knowledge)} 条")
    return all_knowledge

def process_local_medical_txt():
    """处理本地 medical.txt 文件"""
    txt_path = "data/raw/medical.txt"
    
    if not os.path.exists(txt_path):
        print(f"⚠️ 本地文件不存在: {txt_path}")
        return []
    
    print(f"\n📄 处理本地文件: medical.txt")
    
    try:
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        qa_pairs = []
        i = 0
        while i < len(lines) - 1:
            q = lines[i].strip()
            a = lines[i+1].strip() if i+1 < len(lines) else ""
            
            if q and a and len(q) > 5 and len(a) > 5:
                qa_pairs.append({
                    'department': '综合',
                    'title': q[:50],
                    'question': q,
                    'answer': a,
                    'text': f"【综合】{q[:80]}\n回答：{a[:150]}",
                    'source': 'medical.txt'
                })
                i += 2
            else:
                i += 1
        
        print(f"  ✅ 提取 {len(qa_pairs)} 个问答对")
        return qa_pairs[:500]  # 限制数量
        
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")
        return []

def merge_knowledge_base():
    """合并所有知识库"""
    print("=" * 60)
    print("合并知识库")
    print("=" * 60)
    
    # 1. 加载原有知识库
    existing_kb = []
    kb_path = "data/medical_knowledge/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r', encoding='utf-8') as f:
            existing_kb = json.load(f)
        print(f"✅ 原有知识库: {len(existing_kb)} 条")
    
    # 2. 处理本地 medical.txt
    local_kb = process_local_medical_txt()
    
    # 3. 处理护理文件
    nursing_kb = process_nursing_files()
    
    # 4. 合并
    merged_kb = existing_kb + local_kb + nursing_kb
    
    print(f"\n📊 合并后总计: {len(merged_kb)} 条")
    print(f"  - 原有医疗数据: {len(existing_kb)} 条")
    print(f"  - 本地数据: {len(local_kb)} 条")
    print(f"  - 护理数据: {len(nursing_kb)} 条")
    
    # 5. 保存
    output_path = "data/medical_knowledge/knowledge_base_merged.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_kb, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 合并知识库已保存: {output_path}")
    print(f"📦 文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    
    # 6. 替换原知识库
    import shutil
    shutil.copy(output_path, kb_path)
    print(f"✅ 已更新主知识库")
    
    return merged_kb

if __name__ == "__main__":
    merge_knowledge_base()
