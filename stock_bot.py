import requests

# ==================== 改成你自己的 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"
# 自选股票（只支持 A股 代码）
STOCKS = [
    "000001",
    "000858",
    "600519",
    "000063"
]
ALERT_RATIO = 2.0
# ======================================================

def get_stock(code):
    try:
        # 这个接口 GitHub 绝对能用！
        url = f"https://qt.gtimg.cn/q=s_{code}"
        res = requests.get(url, timeout=10)
        s = res.text

        # 解析数据
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
    msg = "📈 A股定时行情推送\n——————————————\n"
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

    send_wechat("股票播报", msg)
    if alert_msg:
        send_wechat("异动提醒", alert_msg)

if __name__ == "__main__":
    run()
