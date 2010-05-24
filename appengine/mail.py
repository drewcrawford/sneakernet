#!/usr/bin/env python

from google.appengine.api import mail
import logging
FROM_MAIL_ADDRESS="whatever@whatever.com"
ALERT_ADMIN_ADDRESS="whatever@whatever.com"


def send_mail(to,subject,msg,sneakfile=None):
    import logging
    logging.info(msg)
    logging.info(sneakfile)
    if sneakfile!=None:
        mail.send_mail(sender=FROM_MAIL_ADDRESS,to=to,subject=subject,body=msg,attachments=[("openthis.sneak",sneakfile)])
    else:
        mail.send_mail(sender=FROM_MAIL_ADDRESS,to=to,subject=subject,body=msg)
def alert_admins(msg):
    from random import choice
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    errorcode = ""
    for i in range(0,32):
        errorcode += choice(chars)
    msg += "\nError code: " + errorcode
    logging.error("Error code: " + errorcode)
    send_mail(to=ALERT_ADMIN_ADDRESS,subject="SNEAKERNET CRITICAL ERROR",msg=msg)