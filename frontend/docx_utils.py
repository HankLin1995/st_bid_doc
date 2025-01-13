
from docx import Document

def replace_text_within_percent_signs(file_path, replace_dict):
    
    try:
        doc = Document(file_path)
        
        for para in doc.paragraphs:
            replace_in_paragraph(para, replace_dict)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_in_paragraph(paragraph, replace_dict)

        doc.save(file_path)

        if check_replaced(file_path, replace_dict)==False:
            return f"文件 {file_path} 有未處理的標記。"
    
    except Exception as e:
        print(f"無法處理文件 {file_path}: {e}")
    
    #shutil.rmtree(tmp_folder_path)  

def replace_in_paragraph(paragraph, replace_dict):
    """基於整段文字進行標記替換，並保留格式。"""
    text = paragraph.text  # 獲取整段文字
    replaced_text = text  # 用於存放替換後的文字

    # 找到所有標記並替換
    for key, value in replace_dict.items():
        replaced_text = replaced_text.replace(f"%%{key}%%", str(value))

    # 如果沒有任何替換，直接返回
    if replaced_text == text:
        return

    # 清空原始 runs
    for run in paragraph.runs:
        paragraph._p.remove(run._element)

    # 將替換後的文字重新加入 paragraph，並保留第一個 run 的格式
    first_run = paragraph.add_run(replaced_text)

    # 保留第一個 run 的格式
    if paragraph.runs:
        original_run = paragraph.runs[0]
        first_run.font.name = original_run.font.name
        first_run.font.size = original_run.font.size
        first_run.font.bold = original_run.font.bold
        first_run.font.italic = original_run.font.italic
        first_run.font.underline = original_run.font.underline
        if hasattr(original_run.font, 'color'):
            first_run.font.color.rgb = original_run.font.color.rgb

# check if the file content is all replaced (contains no %%)

def check_replaced(file_path, replace_dict):
    doc = Document(file_path)
    for para in doc.paragraphs:
        text = para.text
        if "%%" in text:
            return False
        for key in replace_dict.keys():
            if f"%%{key}%%" in text:
                return False

    # print(f"已完成段落替換: {replaced_text}")

