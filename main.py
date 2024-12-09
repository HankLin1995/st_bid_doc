import os
import shutil
from docx import Document


def replace_text_within_percent_signs(file_path, replace_dict, tmp_folder_name):
    tmp_folder_path = os.path.join(os.getcwd(), f"{tmp_folder_name}_TMP")
    
    if not os.path.exists(tmp_folder_path):
        os.makedirs(tmp_folder_path)
    
    file_name = os.path.basename(file_path)
    tmp_file_path = os.path.join(tmp_folder_path, file_name)
    
    shutil.copy(file_path, tmp_file_path)
    
    try:
        doc = Document(tmp_file_path)
        
        for para in doc.paragraphs:
            replace_in_paragraph(para, replace_dict)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_in_paragraph(cell.paragraphs[0], replace_dict)  

        doc.save(tmp_file_path)
    
    except Exception as e:
        print(f"無法處理文件 {tmp_file_path}: {e}")
    
    #shutil.rmtree(tmp_folder_path)  

def replace_in_paragraph(paragraph, replace_dict):
    start_pos = paragraph.text.find("%%")
    while start_pos != -1:
        end_pos = paragraph.text.find("%%", start_pos + 2)
        
        if end_pos != -1:
            target_content = paragraph.text[start_pos + 2:end_pos]
            
            if target_content in replace_dict:
                replace_with = replace_dict[target_content]
                paragraph.text = paragraph.text.replace(f"%%{target_content}%%", replace_with)
            
            start_pos = paragraph.text.find("%%", end_pos + 2)
        else:
            break
