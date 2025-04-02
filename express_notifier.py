# 📦 express_notifier.py

import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

# 从环境变量读取敏感信息
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# 你可以把多个单号写在这里，用逗号分隔（从 GitHub Secrets 中读取）
TRACKING_NUMBERS = os.getenv("TRACKING_NUMBERS", "").split(",")

# 获取快递信息（HTML 格式）
def get_tracking_info(order_no):
    url = "http://47.103.28.217/public/v1/ordeSearch/trackInfo"
    params = {"orderNo": order_no}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.encoding = "utf-8"
        data = res.json()
        if data.get("code") == 200:
            obj = data.get("obj", {})
            info = f"""
            <div style='border:1px solid #ccc;border-radius:8px;padding:12px;margin-bottom:16px;'>
                <h3>📦 单号：{obj.get('orderNo')}</h3>
                <p><strong>🌍 目的国：</strong> {obj.get('country')}</p>
                <p><strong>🚚 派送商：</strong> {obj.get('deliveryCompany')}</p>
                <p><strong>📍 最新轨迹：</strong> {obj.get('lastTrackInfo')}</p>
                <p><strong>📮 邮编：</strong> {obj.get('postCode')}</p>
                <p><strong>🔖 状态：</strong> {obj.get('trackingStatus')}</p>
            </div>
            """
            return info
        else:
            return f"<p style='color:red;'>❗ 单号 {order_no} 查询失败：{data.get('msg')}</p>"
    except Exception as e:
        return f"<p style='color:red;'>⚠️ 查询 {order_no} 出错：{str(e)}</p>"

# 发送 HTML 邮件
def send_email(subject, html_content):
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr(("快递机器人", SENDER_EMAIL))
    msg["To"] = formataddr(("你", RECEIVER_EMAIL))
    msg["Subject"] = Header(subject, "utf-8")

    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        print("✅ 邮件发送成功")
    except Exception as e:
        print("❌ 邮件发送失败：", e)

# 主函数（供 GitHub Actions 使用）
def main():
    html = "<h2>📬 今日快递追踪信息</h2>"
    for number in TRACKING_NUMBERS:
        if number.strip():
            html += get_tracking_info(number.strip())
    send_email("📦 每日快递状态更新", html)

if __name__ == "__main__":
    main()
