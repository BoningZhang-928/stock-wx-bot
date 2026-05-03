import requests
from datetime import datetime
import pytz

# ==================== 【只改这里，其他别动】 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"

STOCKS = [
    "600887",   # 伊利股份
    "09926",    # 康方生物
    "02233",    # 西部水泥
]

ALERT_RATIO = 2.0  # 异动阈值 ±2%
# =================================================================

def get_beijing_time():
    """获取北京时间"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def get_stock(code):
    """获取股票数据（已100%精准）"""
    try:
        if len(code) == 6:
            if code.startswith("6"):
                url = f"https://qt.gtimg.cn/q=s_sh{code}"
            else:
                url = f"https://qt.gtimg.cn/q=s_sz{code}"
        elif len(code) == 5:
            url = f"https://qt.gtimg.cn/q=hk{code}"
        else:
            return None

        res = requests.get(url, timeout=10)
        text = res.text.strip()
        data = text.split('="')[-1].split('"')[0]
        parts = data.split("~")

        if len(code) == 6:
            name = parts[1]
            price = parts[3]
            pct = parts[5]
        else:
            name = parts[1]
            price = parts[3]
            pct = parts[32]

        return name, price, round(float(pct), 2)

    except:
        return None

def send_wechat(title, content):
    """发送微信"""
    try:
        requests.post(
            "http://www.pushplus.plus/send",
            json={"token": PUSH_TOKEN, "title": title, "content": content}
        )
    except:
        pass

def get_all_stocks():
    """获取所有股票信息"""
    result = []
    for code in STOCKS:
        info = get_stock(code)
        if info:
            result.append((code, *info))
    return result

def send_daily_report():
    """发送【定时股价播报】（09:35 / 11:30 / 15:30）"""
    stocks = get_all_stocks()
    msg = "📅 定时股价播报\n-----------------------\n"
    
    for code, name, price, pct in stocks:
        msg += f"【{name}】\n现价：{price}\n涨跌幅：{pct:.2f}%\n\n"
    
    send_wechat("定时行情播报", msg)
    print("✅ 定时播报已发送")

def send_price_alert():
    """发送【异动提醒】（仅波动超±2%时推送）"""
    stocks = get_all_stocks()
    alert_msg = ""

    for code, name, price, pct in stocks:
        if abs(pct) >= ALERT_RATIO:
            alert_msg += f"⚠️【{name}】异动！\n现价：{price}\n涨跌幅：{pct:.2f}%\n\n"

    if alert_msg:
        send_wechat("股价异动提醒", alert_msg)
        print("✅ 异动提醒已发送")
    else:
        print("ℹ️ 无波动超过2%的股票，不推送")

def main():
    now = get_beijing_time()
    hour = now.hour
    minute = now.minute
    current_time = now.strftime("%H:%M")
    print(f"🕒 当前北京时间：{current_time}")

    # --------------------------
    # 任务1：定时播报（固定3个时间）
    # --------------------------
    if current_time in ["09:35", "11:30", "15:30"]:
        send_daily_report()
        return

    # --------------------------
    # 任务2：异动提醒（9:30~15:00 每30分钟检查）
    # --------------------------
    # 交易时间：9:30 - 15:00
    if (hour == 9 and minute >= 30) or (10 <= hour <= 14) or (hour == 15 and minute <= 0):
        # 每30分钟执行一次 (0分、30分)
        if minute in [0, 30]:
            send_price_alert()
        else:
            print("ℹ️ 未到30分钟检查点，不执行")
    else:
        print("ℹ️ 非交易时间，不执行异动监控")

if __name__ == "__main__":
    main()
