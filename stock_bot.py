import requests

# ==================== 【只改这里，其他别动】 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"

STOCKS = [
    "SH600887",   # 伊利股份（A股）
    "09926",    # 康方生物（港股）
    "02233",    # 西部水泥（港股）
]

ALERT_RATIO = 2.0
# =================================================================

def get_stock(code):
    try:
        if len(code) == 6:
            # A股：s_sh / s_sz
            if code.startswith("6"):
                url = f"https://qt.gtimg.cn/q=s_sh{code}"
            else:
                url = f"https://qt.gtimg.cn/q=s_sz{code}"
        elif len(code) == 5:
            # 港股：hk
            url = f"https://qt.gtimg.cn/q=hk{code}"
        else:
            return None

        res = requests.get(url, timeout=8)
        text = res.text.strip()

        # 去掉头部 v_s_sh600887=" 和尾部 "
        if "=" not in text or "\"" not in text:
            return None
        data = text.split("=\"")[-1].rstrip("\"")
        parts = data.split("~")
        if len(parts) < 20:
            return None

        # 字段映射（A股/港股分开）
        if len(code) == 6:
            # A股：name=1, price=3, change=4, percent=5
            name = parts[1]
            price = parts[3]
            change = parts[4]
            percent = parts[5]
        else:
            # 港股：name=1, price=3, change=10, percent=9
            name = parts[1]
            price = parts[3]
            change = parts[10]
            percent = parts[9]

        if float(price) <= 0:
            return None

        return name, price, float(percent)

    except Exception as e:
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
        info = get_stock(code)

        if not info:
            msg += f"❌ {code} 获取失败\n\n"
            continue

        name, price, pct = info
        msg += f"【{name}】\n现价：{price}\n涨跌幅：{pct:.2f}%\n\n"

        if abs(pct) >= ALERT_RATIO:
            alert += f"⚠️ {name} 波动超 {ALERT_RATIO}%\n"

    send_wechat("股票定时推送", msg)
    if alert:
        send_wechat("异动提醒", alert)

if __name__ == "__main__":
    main()
