required_login = [
    "/dashboard", 
    "/song_choice",
    "/admin_songs",
    "/arrange",
]

auth = ["站长", "节目副站", "线上节目总监", "线下节目总监", "主持副站", "主持总监", "宣传副站", "宣传总监", "声带副站", "声带总监", "技术副站", "技术总监", "高干", "站员"]

def program_id(id):
    week = ""
    day = ""
    period = ""
    if (id//100)==1:
        week = "单周"
    else:
        week = "双周"
    day_list = ["一", "二", "三", "四", "五"]
    day = day_list[((id%100)//10)-1]
    if id%10 == 1:
        period = "上午"
    else:
        period = "下午"

    return week+"周"+day+period
