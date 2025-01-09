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
    
