import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "BINB Test Delivery"
    msg['From'] = "Brandon Is Not Boring <truekin.app@gmail.com>"
    msg['To'] = "truekin.app@gmail.com"
    msg.attach(MIMEText("Test email successful!", 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login("truekin.app@gmail.com", "jqhg ebjg uonv sqgb")
    server.sendmail("truekin.app@gmail.com", "truekin.app@gmail.com", msg.as_string())
    server.quit()
    print("Gmail 587 login and send SUCCESSFUL")
except Exception as e:
    print(f"Gmail SMTP Error: {e}")
