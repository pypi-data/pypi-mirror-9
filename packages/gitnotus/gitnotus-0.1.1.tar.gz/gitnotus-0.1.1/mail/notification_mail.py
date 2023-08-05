#!/usr/bin/env python
# Import smtplib for the actual sending function
import smtplib
import time
import datetime
# Import the email modules we'll need
from email.mime.text import MIMEText

#==============================================================================
# Variables
#==============================================================================

# Some descriptive variables
#name                = "gitnotus"
#version             = "0.1.0"
#long_description    = """gitnotus is a set of API's/tools written to manage github events."""
#url                 = "https://github.com/dineshappavoo/gitnotus"
#license             = ""

#==============================================================================


to_address = ''

def send_notification_mail(subject, content, to_email):
    #try:
        #Activity Log
        #vmmail_log = open('/var/lib/virtdc/logs/activity_logs/vmmail.log', 'a+')
        # Create a text/plain message
        #msg = MIMEText(content)
        msg = MIMEText(content, 'plain')

        #text.attach(content)
        
        from_address = 'gitnotus@gmail.com'
        to_address = [to_email]
        #['dinesh.appavoo@utdallas.edu','imaginejhm@gmail.com','rxw130330@utdallas.edu','qxd130530@utdallas.edu','rkn130030@utdallas.edu']
        
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = ",".join(to_address)
        
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        
        username = 'gitnotus'
        password = '1dineshta'
        
        #start smtp server by this command 'python -m smtpd -n -c DebuggingServer localhost:1025'
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(username,password)
        s.sendmail(from_address, to_address, msg.as_string())
        s.quit()
        #vmmail_log.write(str(datetime.datetime.now()) +'Mail to support ::'+str(to_address)+' :: Successfully sent\n')
        
        #except Exception, e:
        #print str(datetime.datetime.now()) +'Mail to support ::'+str(to_address)+' :: Failed\n'
        #vmmail_log.write(str(datetime.datetime.now()) +'Mail to support ::'+str(to_address)+' :: Failed\n')


if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    #fp = open('/var/lib/virtdc/mail/textfile.py', 'rb')
    send_notification_mail('Test','Test Content', 'dinesha.cit@gmail.com')
