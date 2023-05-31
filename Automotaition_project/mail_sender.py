import os
from dotenv import load_dotenv
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText


class Email:

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    smtp_server = os.environ['SMTP_SERVER']
    smtp_sender = os.environ['SMTP_LOGIN']
    smtp_pass = os.environ['SMTP_PASSWORD']

    @classmethod
    def send_message(cls, receiver: str, name: str, login: str, password: str):
        try:
            # typical values for text_subtype are plain, html, xml
            text_subtype = 'plain'
            content = """
            Добрый день, %s
             
            Вам был предоставлен доступ к порталу поддержки Itop. 
            
            Ссылка для входа - https://itop.ru/pages/UI.php
            
            Login: %s ,
            password: %s
            
            Пароль при первом входе будет предложено сменить.
            """ % (name, login, password)

            subject = "Доступ к порталу поддержки Itop"

            msg = MIMEText(content, text_subtype)
            msg['Subject'] = subject
            msg['From'] = cls.smtp_sender

            conn = SMTP(cls.smtp_server)
            conn.set_debuglevel(False)
            conn.login(cls.smtp_sender, cls.smtp_pass)
            try:
                conn.sendmail(cls.smtp_sender, receiver, msg.as_string())
            finally:
                conn.quit()
            return 'Message sent successfully'
        except Exception as e:
            print(str(e))
