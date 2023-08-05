__author__ = 'negash'
# coding=utf-8
from libK.kernel import kernel
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
import os
from smtplib import SMTP_SSL


def mail(array):
    keys = array.keys()
    if 'from' in keys:
        if 'text' in keys:
            if array['from'] in kernel['mail'].keys():
                address = kernel['mail'][array['from']]['user']

                # Compose message
                msg = MIMEMultipart()
                if 'subject' in keys:
                    msg['Subject'] = array['subject']
                msg['From'] = address
                msg['To'] = ', '.join(kernel['mailTo'])
                text = MIMEText(array['text'], 'html')
                msg.attach(text)
                # Compose attachment
                if 'files' in keys:
                    for filepath in array['files']:
                        basename = os.path.basename(filepath)
                        part = MIMEBase('application', "octet-stream")
                        part.set_payload(open(filepath, "rb").read())
                        Encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment; filename="%s"' % basename)
                        msg.attach(part)

                # Send mail
                smtp = SMTP_SSL()
                smtp.connect(kernel['mail'][array['from']]['host'], kernel['mail'][array['from']]['port'])
                smtp.login(address, kernel['mail'][array['from']]['password'])
                smtp.sendmail(address, kernel['mailTo'], msg.as_string())
                smtp.quit()
                return True
            else:
                return {"error": "'" + array['from'] + "' not in kernel['mail']"}
        else:
            return {"error": "need in 'text'"}
    else:
        return {"error": "need in 'from'"}
