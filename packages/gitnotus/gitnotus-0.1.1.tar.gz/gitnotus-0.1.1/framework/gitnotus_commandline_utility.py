#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import time
from repo_maintainer import update_dict, GetUserDict

#API - gitnotus command line interface

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

def add_repo(uname, repo_name, email):
    update_dict(uname, repo_name, email)
    print '''\nRepo successfully added. Please use this URL to add a webhook to your repository "https://5ef548a0.ngrok.com/" \n'''

def get_user_info(uname):
    user_dict=GetUserDict()
    for user in user_dict:
        user_obj = user_dict[uname]
        if user_obj!= None:
            print '%s%s' %(str('User Name:').ljust(30),uname)
            print '--------------------------------------------'
            print '%s%s' %(str('Repository name :').ljust(30),user_obj.repo_name)
            print '%s%s' %(str('Email Address : ').ljust(30),user_obj.email_address)

        #print '--------------------------------------------'
            return True
        else:
            return False

def getall_user_info():
    user_dict=GetUserDict()
    print '%s%s%s' %(str('User Name').ljust(25),str('Repo Name').ljust(25),'Email Address')
    print '---------------------------------------------------------------------------'
    for user in user_dict:
        user_obj = user_dict[user]
        print '%s%s%s' %(str(user).ljust(25),str(user_obj.repo_name).ljust(25),str(user_obj.email_address).ljust(50),)

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    #add_repo('maximus11', 'video_analytics', 'Rahul.1186@gmail.com ')
    #get_user_info('maximus11')
    getall_user_info()