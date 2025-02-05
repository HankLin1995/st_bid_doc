def num_to_chinese(amount):

    import cn2an
    import opencc

    if amount==0: return "免收"

    cc = opencc.OpenCC('s2t')  # 's2t' 表示简体转繁体
    simplified_text=cn2an.an2cn(str(amount),"up")
    simplified_text= simplified_text.replace("叁","參")
    return cc.convert(simplified_text)+'元整'

def get_contractor(contract_money: float) -> str:
    m = contract_money

    if m <= 6000000:
        f = "設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業"

    elif 6000000 < m <= 7200000:
        f = "設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業"

    elif m <= 22500000:
        #f = "丙等(含)以上綜合營造業"
        f = "丙等以上綜合營造業"

    elif 22500000 < m <= 27000000:
        f = "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業"

    elif m <= 75000000:
        #f = "乙等(含)以上綜合營造業"
        f = "乙等以上綜合營造業"

    elif 75000000 < m <= 90000000:
        f = "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業"

    else:
        #f = "甲等(含)以上綜合營造業"
        f = "甲等綜合營造業"

    result = f

    # # Check specific contract money cases and add a special prefix
    # if m in [6000000, 7200000, 22500000, 27000000, 75000000, 90000000]:
    #     result = "!!!!!!!!!!" + f

    return result

def get_cost_range(contract_money: float) -> str:

    if contract_money < 150000:
        return "公告金額十分之一之採購"
    elif contract_money < 1500000:
        return "未達公告金額而逾公告金額十分之一之採購"
    elif contract_money < 50000000:
        return "公告金額以上未達查核金額之採購"
    else:
        return "查核金額以上未達巨額之採購"

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

def get_work_type(work_type, work_days):
    general_box = False
    specified_box = False
    runoff_box = False
    general_date= None
    specified_date= None
    runoff_date= None

    if work_type == "一般流程":
        general_box = True
        general_date = work_days
    elif work_type == "指定開工日":
        specified_box = True
        specified_date = work_days
        # start_date = st.date_input("指定開工日")
    elif work_type == "逕流廢汙水":
        runoff_box = True
        runoff_date = work_days

    return general_box, specified_box, runoff_box, general_date, specified_date, runoff_date

def get_cost_type(cost_type: str):

    purchase_a = False
    purchase_b = False
    purchase_c = False

    if cost_type == "未達公告金額而逾公告金額十分之一之採購":
        purchase_a = True
    elif cost_type == "公告金額以上未達查核金額之採購":
        purchase_b = True
    elif cost_type == "查核金額以上未達巨額之採購":
        purchase_c = True
    else:
        st.toast("小額採購或巨額採購請另外處理!!!",icon="🚫")
    
    return purchase_a, purchase_b, purchase_c

def get_employ_type(qualification: str):
    # Initially set all checkboxes to False
    contractor_a = False
    contractor_a1 = False
    contractor_a2 =False
    contractor_a3 = False
    contractor_b = False

    # Classifying based on qualification type and selecting appropriate checkboxes
    if qualification == "設立於雲林縣或毗鄰縣市之土木包工業，或丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher, so select "廠商A丙-BOX"
        contractor_b = True  # 土包 as well
        
    elif qualification == "設立於雲林縣或毗鄰縣市並依營造業法規定辦理資本額增資之土木包工業，或丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher
        contractor_b = True  # 土包
        
    elif qualification == "丙等以上綜合營造業":
        contractor_a = True
        contractor_a3 = True  # 丙等 or higher
    
    elif qualification == "依營造業法規定辦理資本額增資之丙等綜合營造業，或乙等以上綜合營造業":
        contractor_a = True
        contractor_a2 = True
        contractor_a3 = True  # 乙等 or higher
        
    elif qualification == "乙等以上綜合營造業":
        contractor_a = True
        contractor_a2 = True  # 乙等 or higher

    elif qualification == "依營造業法規定辦理資本額增資之乙等綜合營造業，或甲等以上綜合營造業":
        contractor_a = True
        contractor_a1 = True
        contractor_a2 = True
    
    elif qualification == "甲等綜合營造業":
        contractor_a = True
        contractor_a1 = True

    else:
        st.toast("小額採購或巨額採購請另外處理!!!",icon="🚫")

    return contractor_a, contractor_a1, contractor_a2, contractor_a3, contractor_b
