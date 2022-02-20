import smtplib
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, gmail_password: str, send_to, subject, text, files=None,
              server="smtp.gmail.com", port=587):
    assert isinstance(send_to, list)
    print("emailing edition")
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Cc'] = COMMASPACE.join([send_from])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        print(f)
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    smtp.ehlo()
    smtp.starttls()  # enable security
    smtp.login(send_from, gmail_password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()