from dataclasses import dataclass
from dotenv import load_dotenv
from os import environ
from email.message import EmailMessage
import smtplib
import requests
import time
from datetime import datetime as dt


@dataclass
class Conf:
    sender_email: str
    sender_password: str
    interval_minutes: int
    smtp_server: str
    smtp_port: int
    url: str
    recipients: list[str]


_ = load_dotenv(".env")
conf = Conf(
    sender_email=environ["SENDER_EMAIL"],
    sender_password=environ["SENDER_PASSWORD"],
    interval_minutes=5,
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    url="https://vaapenregisteret.brreg.no/",
    recipients=["james@jamesplank.co.uk"],
)


def send_alert(conf: Conf, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = conf.sender_email
    msg["To"] = ", ".join(conf.recipients)
    msg.set_content(body)

    with smtplib.SMTP(conf.smtp_server, conf.smtp_port) as server:
        _ = server.starttls()
        _ = server.login(conf.sender_email, conf.sender_password)
        _ = server.send_message(msg)


def check_site(conf: Conf) -> bool:
    try:
        res = requests.get(conf.url, timeout=5)
        if res.status_code == 200:
            send_alert(
                conf,
                subject=f"Site {conf.url} is Up!",
                body=f"Response received:\n{res.content}",
            )
            return True
    except requests.RequestException:
        pass
    return False


if __name__ == "__main__":
    still_down = True
    while still_down:
        print(f"Pinging {conf.url}")
        still_down = not check_site(conf=conf)
        if still_down:
            print(f"{dt.now():%Y-%m-%d %H:%M:%S}\tSite is not up")
        else:
            print(f"{dt.now():%Y-%m-%d %H:%M:%S}\t{conf.url} is up!")
        time.sleep(5)
