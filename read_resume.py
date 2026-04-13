"""
读取简历PDF并生成更新后的简历
"""
from pypdf import PdfReader
import os

def read_resume():
    """读取简历内容"""
    pdf_path = os.path.expanduser("~/Desktop/黑白色极简风个人求职简历.pdf")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    return text

if __name__ == "__main__":
    content = read_resume()
    print(content)
