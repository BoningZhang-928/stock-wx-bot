import requests

# ==================== 改成你自己的 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"
# 自选股票：
# A股 直接写代码   例：000001
# 港股 加 hk       例：hk00700
STOCKS = [
    "600887",   # 伊利股份
    "HK09926",   # 康方生物
    "HK02233",  # 西部水泥
]
ALERT_RATIO = 2.0
# ======================================================

def get_stock(code):
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        res = requests.get(url, timeout=10)
        s = res.text

        arr = s.split("~")
        name = arr[1]
        price = arr[3]
        change = arr[8]
        percent = arr[9]

        return {
            "name": name,
            "price": price,
            "percent": float(percent)
        }
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

def run():
    msg = "📈 A股 + 港股 定时行情\n——————————————\n"
    alert_msg = ""

    for code in STOCKS:
        info = get_stock(code)
        if not info:
            msg += f"{code} → 获取失败\n"
            continue

        name = info["name"]
        price = info["price"]
        pct = info["percent"]

        msg += f"{name}\n现价：{price} 元\n涨跌幅：{pct:.2f}%\n\n"

        if abs(pct) >= ALERT_RATIO:
            alert_msg += f"⚠️ {name} 波动超 {ALERT_RATIO}%！\n"

    send_wechat("股票行情播报", msg)
    if alert_msg:
        send_wechat("异动提醒", alert_msg)

if __name__ == "__main__":
    run()
