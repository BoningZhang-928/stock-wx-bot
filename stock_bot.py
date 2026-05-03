import requests

# ==================== 【只改这里，其他别动】 ====================
PUSH_TOKEN = "这里填入你的PushPlus Token"

# 正确写法：
# A股：直接代码
# 港股：必须是 00700（不要hk！不要大写！纯数字！）
STOCKS = [
    "600887",   # 伊利股份
    "09926",   # 康方生物
    "02233",  # 西部水泥
]

ALERT_RATIO = 2.0
# =================================================================

def get_a_stock(code):
    try:
        url = f"https://hq.cninfo.com.cn/query.php?code={code}"
        res = requests.get(url, timeout=10)
        data = res.json()
        name = data["stockName"]
        price = data["lastPrice"]
        change = data["change"]
        percent = data["changePercent"]
        return name, price, float(percent)
    except:
        return None

def get_hk_stock(code):
    try:
        url = f"https://hq.cninfo.com.cn/query.php?code=hk{code}"
        res = requests.get(url, timeout=10)
        data = res.json()
        name = data["stockName"]
        price = data["lastPrice"]
        change = data["change"]
        percent = data["changePercent"]
        return name, price, float(percent)
    except:
        return None

def send_wechat(title, content):
    try:
        requests.post(
            "http://www.pushplus.plus/send",
            json={
                "token": PUSH_TOKEN,
                "title": title,
                "content": content
            }
        )
    except:
        pass

def main():
    msg = "📈 股票行情播报（A股+港股）\n-----------------------\n"
    alert = ""

    for code in STOCKS:
        info = None

        if len(code) == 5:
            # 5位 = 港股
            info = get_hk_stock(code)
        elif len(code) == 6:
            # 6位 = A股
            info = get_a_stock(code)

        if not info:
            msg += f"❌ {code} 获取失败\n\n"
            continue

        name, price, pct = info
        msg += f"【{name}】\n现价：{price} 元\n涨跌幅：{pct:.2f}%\n\n"

        if abs(pct) >= ALERT_RATIO:
            alert += f"⚠️ {name} 波动超 {ALERT_RATIO}%\n"

    send_wechat("股票定时推送", msg)
    if alert:
        send_wechat("异动提醒", alert)

if __name__ == "__main__":
    main()
