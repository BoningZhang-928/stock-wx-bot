import requests

# ==================== 【只改这里，其他别动】 ====================
PUSH_TOKEN = "8cbcd99528f64aaca47ca088bd23de5c"

# 正确写法：
# A股：直接代码
# 港股：必须是 00700（不要hk！不要大写！纯数字！）
STOCKS = [
    "600887",   # 伊利股份
    "09926",    # 康方生物
    "02233",    # 西部水泥
]

ALERT_RATIO = 2.0
# =================================================================

def get_stock(code):
    """
    统一接口：自动识别 A股/港股，稳定可用
    """
    try:
        # 自动判断市场
        if len(code) == 6:
            # A股：sh + 代码 / sz + 代码 都支持
            url = f"https://qt.gtimg.cn/q=s_{code}"
        elif len(code) == 5:
            # 港股：hk + 代码
            url = f"https://qt.gtimg.cn/q=hk{code}"
        else:
            return None

        res = requests.get(url, timeout=8)
        text = res.text.strip()

        # 解析数据
        parts = text.split("~")
        if len(parts) < 30:
            return None

        name = parts[1]
        price = parts[3]
        change = parts[8]
        percent = parts[9]

        # 处理异常价格
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
        msg += f"【{name}】\n现价：{price} 元\n涨跌幅：{pct:.2f}%\n\n"

        if abs(pct) >= ALERT_RATIO:
            alert += f"⚠️ {name} 波动超 {ALERT_RATIO}%\n"

    send_wechat("股票定时推送", msg)
    if alert:
        send_wechat("异动提醒", alert)

if __name__ == "__main__":
    main()
