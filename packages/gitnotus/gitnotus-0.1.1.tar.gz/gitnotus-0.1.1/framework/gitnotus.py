#!/usr/bin/env python
import argparse
import sys, os
from gitnotus_commandline_utility import add_repo, get_user_info, getall_user_info

#API - gitnotus command line tool

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

def main(argv):
    parser = argparse.ArgumentParser(description="A github event notification API", version='gitnotus 0.1.0')
    subparsers = parser.add_subparsers(help='Grouped command', dest='subparser_name')

    addrepo_parser = subparsers.add_parser('addrepo',help='add new repository')
    addrepo_parser.add_argument('username', action = 'store', help ='get the user name')
    addrepo_parser.add_argument('reponame', action = 'store', help ='get the repository name')
    addrepo_parser.add_argument('email', action = 'store', help ='get the email address')

    
    listinfo_parser = subparsers.add_parser('listinfo',help='get all user and repo info')

    userinfo_parser = subparsers.add_parser('userinfo',help='display user info')
    userinfo_parser.add_argument('username', action = 'store', help ='get the user name')

    list_parser = subparsers.add_parser('list',help='list existing domain')


    args = parser.parse_args()

    if args.subparser_name == 'addrepo':
        #print 'Call addrepo domain'
        user_name =args.username
        repo_name = args.reponame
        email_address = args.email
        add_repo(user_name, repo_name, email_address)
    elif args.subparser_name == 'listinfo':
        getall_user_info()
		
    elif args.subparser_name == 'userinfo':
        #print 'Call vmonere remove domain'
        user_name = args.username
        user_status = get_user_info(user_name)
        if user_status == False:
            print 'The requested user name is not available in the system.'
    elif args.subparser_name == 'list':
        print 'Call vm_list'
    else:
        a=0
    #print args
    #print parser.parse_args(['terminate','Dinesh'])
    #print parser.parse_args(['create','Dinesh','1','64434','53445'])

if __name__ == "__main__":
	main(sys.argv[1:])
