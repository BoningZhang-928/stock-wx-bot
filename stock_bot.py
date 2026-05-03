import requests

# ==================== 【只改这里，其他别动】 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"

STOCKS = [
    "600887",   # 伊利股份
    "09926",    # 康方生物
    "02233",    # 西部水泥
]

ALERT_RATIO = 2.0
# =================================================================

def get_stock(code):
    try:
        # 1. 拼接正确行情地址
        if len(code) == 6:
            # A股：6开头=sh，其他=sz
            if code.startswith("6"):
                url = f"https://qt.gtimg.cn/q=s_sh{code}"
            else:
                url = f"https://qt.gtimg.cn/q=s_sz{code}"
        elif len(code) == 5:
            # 港股
            url = f"https://qt.gtimg.cn/q=hk{code}"
        else:
            return None

        # 2. 获取数据
        res = requests.get(url, timeout=8)
        text = res.text.strip()
        if '="' not in text:
            return None
        
        data = text.split('="')[-1].split('"')[0]
        parts = data.split("~")

        # 3. A股 和 港股 字段完全分开！！！
        if len(code) == 6:
            # A 股 正确字段
            name = parts[1]
            price = parts[3]
            percent = parts[5]  # 涨跌幅
        else:
            # 港 股 正确字段（真正的涨跌幅！）
            name = parts[1]
            price = parts[3]
            percent = parts[31]

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

    # 这里已修复：STOCKS ✅
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
