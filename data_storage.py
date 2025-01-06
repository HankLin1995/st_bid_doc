import os
from main import replace_text_within_percent_signs

# 在匯入 data 前進行轉換
def convert_data(data):
    for key in data:
        if isinstance(data[key], bool):
            data[key] = deal_bool(data[key])  # 使用 deal_bool 函數進行轉換
        elif data[key] is None:
            data[key] = ''  # 將 None 轉換為空字符串
    return data

# deal true or false black square or blank square
def deal_bool(data):
    if data:
        return '■'  # 黑色方格
    else:
        return '□'  # 白色方格


# def test_data():

# data = {  # 這裡是你的資料結構
#     '標案名稱': '114年度舊庄農地重劃區小排20等緊急農水路改善工程',
#     '標案案號': '雲林113J206',
#     '年度': '113',
#     '經費來源': '固定資產建設改良擴充-土地改良物(國庫撥款)',
#     '押標金金額': '480000',
#     '押標金金額中文': '肆拾捌萬元整',
#     '廠商資格': '丙等(含)綜合營造業以上',
#     '工程地點': '雲林縣大埤鄉',
#     '預算金額': '9738000',
#     '採購金額上限': None,
#     '採購級距': '公告金額以上未達查核金額之採購',
#     '履約保證金': '970000',
#     '履約保證金中文': '玖拾柒萬元整',
#     '開工型式': None,
#     '工期': '145',
#     '指定開工日': None,
#     '一般BOX': False,
#     '指定BOX': False,
#     '逕流BOX': True,
#     '一般工期': None,
#     '指定工期': None,
#     '逕流工期': '145',
#     '採購A-BOX': False,
#     '採購B-BOX': True,
#     '採購C-BOX': False,
#     '廠商A-BOX': True,
#     '廠商A甲-BOX': False,
#     '廠商A乙-BOX': False,
#     '廠商A丙-BOX': True,
#     '廠商B土包-BOX': False
# }

# data = convert_data(data)  # 進行轉換

# # print(data)

# target_folder=r'D:\Python\st_docx\src\廠商投標表單'

# # loop all file
# for root, dirs, files in os.walk(target_folder):
#     for file in files:
#         if file.endswith(".docx"):
#             file_path = os.path.join(root, file)
#             print(file_path)
#             replace_text_within_percent_signs(file_path, data,data["標案名稱"])
