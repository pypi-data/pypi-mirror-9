#!/usr/bin/env python

import sys
sys.path.append('/Users/Dany/Documents/gitnotus/mail')

from notification_mail import send_notification_mail
from json_parser import format_json
from repo_maintainer import is_repo_available_returnmail
from flask import Flask, request
import json
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

app = Flask(__name__)

@app.route('/',methods=['POST'])
def foo():
    data = json.loads(request.data)
    author = data['commits'][0]['author']['name']
    print "New commit by: "+str(author)
    author_email = data['commits'][0]['author']['email']
    print author_email
    
    repo_name = data['repository']['name']
    print repo_name

    pusher = data['pusher']['name']
    print "Pusher :"+str(pusher)
    pusher_email = data['pusher']['email']
    print "Pusher Email :"+str(pusher_email)
    
    commit_message =data['head_commit']['message']
    print "Commit Message : "+str(commit_message)
    
    #Get email address by passing repo_name
    email_address = is_repo_available_returnmail(repo_name)
    
    if email_address == None :
        pass
    else:
        #call email service
        mail_content = format_json(data)
        invoke_email('push', repo_name, mail_content, email_address)
    return "OK"

def invoke_email(event_type, repo_name, mail_content, to_email):
    mail_subject = 'Git event occured on repository : '+str(repo_name)
    mail_content = str(mail_content).strip()
    send_notification_mail(mail_subject, mail_content, to_email)

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8080)