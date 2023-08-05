import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import charset
from email.charset import Charset
from email.generator import Generator
import io


def send(email_receivers, stories):
    charset.add_charset('utf-8', charset.QP, charset.QP)

    sender = 'salvitobot'

    for story in stories:
        for recipient in email_receivers:
            multipart = MIMEMultipart('alternative')
            multipart['Subject'] = Header(story['title'].encode('utf-8'), 'UTF-8').encode()
            multipart['To'] = Header(recipient.encode('utf-8'), 'UTF-8').encode()
            multipart['From'] = Header(sender.encode('utf-8'), 'UTF-8').encode()

            textpart = MIMEText(story['body'], 'plain', 'UTF-8')
            multipart.attach(textpart)

            mystream = io.StringIO()
            g = Generator(mystream, False)
            g.flatten(multipart)

            message = mystream.getvalue()

            try:
                smtpObj = smtplib.SMTP('localhost')
                smtpObj.sendmail(sender, recipient, message)
                message_to_user = "\nSuccessfully sent email.\n" \
                                  "Probably it went to your SPAM folder.\n" \
                                  "If you are using Gmail you might need to create a filter\n" \
                                  "to avoid sending emails from <salvitobot@aniversarioperu.me> to \n" \
                                  "your SPAM folder. More info here https://support.google.com/mail/answer/6579\n"
                print(message_to_user)
            except smtplib.SMTPException:
                print("Error: unable to send email")
