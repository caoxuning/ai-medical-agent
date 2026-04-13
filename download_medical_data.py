"""
下载并处理中文医疗对话数据集
"""
import os
import urllib.request
import zipfile
import json
import csv

def download_dataset():
    """下载数据集"""
    url = "https://github.com/Toyhom/Chinese-medical-dialogue-data/archive/refs/heads/master.zip"
    output_path = "data/medical_knowledge/medical_data.zip"
    
    print("正在下载中文医疗对话数据集...")
    print(f"来源: {url}")
    
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ 下载完成: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def extract_dataset(zip_path):
    """解压数据集"""
    extract_path = "data/medical_knowledge/"
    
    print("\n正在解压...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"✅ 解压完成")
        return True
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return False

def process_data():
    """处理数据为知识库格式"""
    data_dir = "data/medical_knowledge/Chinese-medical-dialogue-data-master/"
    
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        return None
    
    print("\n正在处理数据...")
    
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
    total_records = 0
    
    for folder, dept_name in departments:
        csv_path = os.path.join(data_dir, folder, f"{folder}.csv")
        
        if not os.path.exists(csv_path):
            print(f"⚠️ 跳过 {dept_name}: 文件不存在")
            continue
        
        print(f"📂 处理 {dept_name}...")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                
                for row in reader:
                    # 构建知识条目
                    knowledge_entry = {
                        "department": dept_name,
                        "title": row.get("title", ""),
                        "question": row.get("question", ""),
                        "answer": row.get("answer", ""),
                        "text": f"【{dept_name}】{row.get('title', '')}\n问题：{row.get('question', '')}\n回答：{row.get('answer', '')}"
                    }
                    
                    knowledge_base.append(knowledge_entry)
                    count += 1
                    
                    # 每个科室只取前 1000 条（演示用）
                    if count >= 1000:
                        break
                
                total_records += count
                print(f"  ✅ {dept_name}: {count} 条记录")
                
        except Exception as e:
            print(f"  ❌ {dept_name} 处理失败: {e}")
    
    print(f"\n📊 总计处理: {total_records} 条记录")
    
    # 保存为 JSON
    output_file = "data/medical_knowledge/knowledge_base.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 知识库已保存: {output_file}")
    return knowledge_base

if __name__ == "__main__":
    # 下载
    zip_path = download_dataset()
    
    if zip_path and os.path.exists(zip_path):
        # 解压
        if extract_dataset(zip_path):
            # 处理
            process_data()
        else:
            print("\n⚠️ 尝试使用已有数据...")
            process_data()
    else:
        print("\n⚠️ 下载失败，尝试使用已有数据...")
        process_data()
