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