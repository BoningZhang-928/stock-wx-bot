import requests

# ==================== 改成你自己的 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"
# 自选股票 A股/港股/美股
STOCKS = [
    "SH600887",   # 伊利股份
    "HK09926",   # 康方生物
    "HK02233",  # 西部水泥
]
# 异动提醒阈值
ALERT_RATIO = 2.0
# ======================================================

def get_stock_info(code):
    try:
        url = f"https://api.money.126.net/data/feed/{code}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        item = data[code]
        return {
            "name": item["name"],
            "price": item["price"],
            "percent": float(item["percent"])
        }
    except Exception as e:
        return None

def send_wechat(title, content):
    requests.post(
        "http://www.pushplus.plus/send",
        json={
            "token": PUSH_TOKEN,
            "title": title,
            "content": content
        }
    )

def run():
    msg = "📈 每日股票行情简报\n——————————\n"
    alert_msg = ""

    for code in STOCKS:
        info = get_stock_info(code)
        if not info:
            msg += f"{code} 获取失败\n"
            continue
        name = info["name"]
        price = info["price"]
        pct = info["percent"]
        msg += f"{name}｜现价：{price}｜涨跌幅：{pct:.2f}%\n"

        if abs(pct) >= ALERT_RATIO:
            alert_msg += f"⚠️ {name} 异动 {pct:.2f}%\n"

    # 推送日常行情
    send_wechat("股票定时播报", msg)
    # 有异动单独推送
    if alert_msg:
        send_wechat("⚠️ 股票异动提醒", alert_msg)

if __name__ == "__main__":
    run()
