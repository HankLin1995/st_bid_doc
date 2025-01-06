import os
import shutil

def create_folder(doc_folder,output_dir):

    print(doc_folder)
    print(output_dir)

    # doc_folder=r".\src\廠商投標表單"

    # output_dir=r".\output2"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        os.makedirs(output_dir+"\\投標文件")
    else:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        os.makedirs(output_dir+"\\投標文件")

    for root, dirs, files in os.walk(doc_folder):
        for file in files:

            file_path = os.path.join(root, file) # 取得文件的完整路徑
            print("file_path",file_path)
            relative_path = os.path.relpath(file_path, doc_folder) # 取得相對路徑
            print("relative_path",relative_path)
            output_file_path=os.path.join(output_dir,relative_path) # 取得輸出文件的完整路徑
            print("output_file_path",output_file_path)
            shutil.copy(file_path,output_file_path) # 將文件複製到輸出目錄

if __name__ == "__main__":
    create_folder(r".\src\廠商投標表單",r".\output2")