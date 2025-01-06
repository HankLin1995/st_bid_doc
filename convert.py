import os
import win32com.client
from concurrent.futures import ProcessPoolExecutor

## 利用windows的win32com套件將doc轉換成docx

class WordConverter:
    def __init__(self):
        self.word = win32com.client.Dispatch("Word.Application")
        self.word.Visible = False  # 不顯示 Word 應用程序窗口

    def convert_doc_to_docx(self, doc_file, docx_file):
        # 打開 .doc 文件
        doc = self.word.Documents.Open(doc_file)
        print(f'Opened: {doc_file}')  
        # 保存為 .docx 格式
        doc.SaveAs(docx_file, FileFormat=16)  # FileFormat=16 代表 .docx 格式
        # 關閉文件
        doc.Close()

    def quit(self):
        self.word.Quit()

def convert_file(doc_file_path):
    converter = WordConverter()  # 在每次調用時創建新的 WordConverter 實例
    docx_file_path = doc_file_path[:-4] + '.docx'  # 替换文件扩展名
    converter.convert_doc_to_docx(doc_file_path, docx_file_path)
    print(f'Converted: {doc_file_path} to {docx_file_path}')
    # 删除原有的 .doc 文件
    os.remove(doc_file_path)
    converter.quit()

def convert_all_docs_in_directory(directory):
    with ProcessPoolExecutor(max_workers=8) as executor:  # 使用 ProcessPoolExecutor
        for root, dirs, files in os.walk(directory):
            for filename in files:
                print(filename)
                if filename.endswith('.doc'):
                    doc_file_path = os.path.join(root, filename)
                    try:
                        executor.submit(convert_file, doc_file_path)  # 提交任務
                    except Exception as e:
                        print(f'Error converting {doc_file_path}: {e}')  # 錯誤處理

if __name__ == "__main__":
    src_directory = r"D:\Python\st_docx\src"  # 指定源文件夹路径
    print(f"Converting all .doc files in {src_directory}")
    convert_all_docs_in_directory(src_directory)
