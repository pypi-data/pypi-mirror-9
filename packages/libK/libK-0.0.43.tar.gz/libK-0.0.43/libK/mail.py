# coding=utf-8
__author__ = 'negash'
from libK.kernel import kernel
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
import os
from smtplib import SMTP_SSL


def mail(array):
    keys = array.keys()
    if 'from' not in keys:
        return {"error": "need in 'from'"}
    if 'text' not in keys:
        return {"error": "need in 'text'"}
    if array['from'] not in kernel['mail'].keys():
        return {"error": "'" + array['from'] + "' not in kernel['mail']"}
    address = kernel['mail'][array['from']]['user']

    # Compose message
    msg = MIMEMultipart()
    if 'subject' in keys:
        msg['Subject'] = array['subject']
    msg['From'] = address
    if not kernel['mailTo']:
        return {"error": "need in kernel['mailTo']"}
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
    errors = []
    try:
        smtp.connect(kernel['mail'][array['from']]['host'], kernel['mail'][array['from']]['port'])
    except:
        errors.append({"error": "Can't use connect()"})
    try:
        smtp.login(address, kernel['mail'][array['from']]['password'])
    except:
        errors.append({"error": "Can't use login()"})
    try:
        smtp.sendmail(address, kernel['mailTo'], msg.as_string())
    except:
        errors.append({"error": "Can't use sendmail()"})
    try:
        smtp.quit()
    except:
        errors.append({"error": "Can't use quit()"})
    if errors is not []:
        return errors
    return True