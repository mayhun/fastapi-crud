import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

# 템플릿 환경 설정 (templates 폴더 기준)
env = Environment(loader=FileSystemLoader("app/templates"))

def send_email_code(to_email: str, code: str):
    # HTML 템플릿 렌더링
    template = env.get_template("email_verification.html")
    html_content = template.render(code=code)

    subject = "비밀번호 초기화 인증번호"

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[SUCCESS] 인증번호 이메일 전송 완료 → {to_email}")
    except Exception as e:
        print(f"[ERROR] 이메일 전송 실패: {e}")
