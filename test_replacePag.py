import os
import shutil
import main

def copy_file_from_tmp_to_output():

    tmp_folder=r".\src\廠商投標表單"
    output_folder=r".\output2"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        os.makedirs(output_folder+"\\投標文件")
    else:
        shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        os.makedirs(output_folder+"\\投標文件")

    for root, dirs, files in os.walk(tmp_folder):
        for file in files:
            file_path = os.path.join(root, file) # 取得文件的完整路徑
            print("file_path",file_path)
            relative_path = os.path.relpath(file_path, tmp_folder) # 取得相對路徑
            print("relative_path",relative_path)
            output_file_path=os.path.join(output_folder,relative_path) # 取得輸出文件的完整路徑
            print("output_file_path",output_file_path)
            shutil.copy(file_path,output_file_path) # 將文件複製到輸出目錄

def loop_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            print(file)

def get_data():

    import data_storage

    data = {  # 這裡是你的資料結構
        '標案名稱': '114年度舊庄農地重劃區小排20等緊急農水路改善工程',
        '標案案號': '雲林113J206',
        '年度': '113',
        '經費來源': '固定資產建設改良擴充-土地改良物(國庫撥款)',
        '押標金金額': '480000',
        '押標金金額中文': '肆拾捌萬元整',
        '廠商資格': '丙等(含)綜合營造業以上',
        '工程地點': '雲林縣大埤鄉',
        '預算金額': '9738000',
        '採購金額上限': None,
        '採購級距': '公告金額以上未達查核金額之採購',
        '履約保證金': '970000',
        '履約保證金中文': '玖拾柒萬元整',
        '開工型式': None,
        '工期': '145',
        '指定開工日': None,
        '一般BOX': False,
        '指定BOX': False,
        '逕流BOX': True,
        '一般工期': None,
        '指定工期': None,
        '逕流工期': '145',
        '採購A-BOX': False,
        '採購B-BOX': True,
        '採購C-BOX': False,
        '廠商A-BOX': True,
        '廠商A甲-BOX': False,
        '廠商A乙-BOX': False,
        '廠商A丙-BOX': True,
        '廠商B土包-BOX': False
    }

    return data_storage.convert_data(data)

if __name__ == "__main__":

    copy_file_from_tmp_to_output()

    data=get_data()
    output_folder=r".\output2"
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if file.endswith("test.docx"):
                file_path = os.path.join(root, file)
                print(file_path)
                main.replace_text_within_percent_signs(file_path,data)
                
                