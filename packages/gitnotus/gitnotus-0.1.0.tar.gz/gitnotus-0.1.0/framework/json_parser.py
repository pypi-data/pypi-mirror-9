#!/usr/bin/python

import sys
sys.path.append('/Users/Dany/Documents/gitnotus/mail')

from notification_mail import send_notification_mail
import json

def format_json(data):
    mail_content = ''
    #path = '/Users/Dany/Documents/gitnotus/framework/sample.json'
    #with open(path) as hook_file:
        #data = json.load(hook_file)
    #print data
    repo_name = data['repository']['name']
    repo_name = "Repository Name : "+str(repo_name) + '\n'
    mail_content = mail_content + repo_name
    #print repo_name

    author = data['commits'][0]['author']['name']
    author = "Author Name: "+str(author) + '\n'
    mail_content = mail_content + author
    #print author

    author_email = data['commits'][0]['author']['email']
    author_email = "Author Email : "+str(author_email) + '\n'
    mail_content = mail_content +author_email
    #print author_email
    
    pusher = data['pusher']['name']
    pusher = "Pusher : "+str(pusher) + '\n'
    mail_content = mail_content + pusher
    #print pusher

    pusher_email = data['pusher']['email']
    pusher_email = "Pusher Email :"+str(pusher_email) + '\n'
    mail_content = mail_content + pusher_email
    #print pusher_email
    
    commit_message =data['head_commit']['message']
    commit_message = "Commit Message : "+str(commit_message) + '\n'
    mail_content = mail_content + commit_message
    #print commit_message

    commit_time = data['head_commit']['timestamp']
    commit_time = "Commit Time : "+str(commit_time) + '\n\n'
    mail_content = mail_content + commit_time
    #print commit_time

    added_files = data['head_commit']['added']
    deleted_files = data['head_commit']['removed']
    modified_files = data['head_commit']['modified']

    add_count = len(added_files)
    del_count = len(deleted_files)
    mod_count = len(modified_files)

    mail_content = mail_content + "Number of newly added Files : "+str(add_count) + '\n'
    if add_count>0:
        mail_content = mail_content + "List of newly added Files : "+'\n'
    for file in added_files:
        #print file + str('\n')
        mail_content = mail_content + '\t' + file + '\n'

    mail_content = mail_content + "Number of deleted Files : "+str(del_count) + '\n'
    if del_count>0:
        mail_content = mail_content + "List of deleted Files : "+'\n'
    for file in deleted_files:
        #print file + str('\n')
        mail_content = mail_content + '\t' + file + '\n'

    mail_content = mail_content + "Number of modified Files : "+str(mod_count) + '\n'
    if mod_count>0:
        mail_content = mail_content + "List of modified Files : "+ '\n'
    for file in modified_files:
        #print file + str('\n')
        mail_content = mail_content + '\t' + file + '\n'

    print mail_content
    return mail_content


def invoke_email(event_type, repo_name):
    #if event_type == 'push'
    mail_subject = 'Git event occured on repository : '+str(repo_name)
    mail_content = format_json()
    mail_content = str(mail_content).strip()
    send_notification_mail(mail_subject, mail_content)


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   #call email service
    invoke_email('push', 'labineer')



	

