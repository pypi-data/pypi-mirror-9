#!/usr/bin/python

import pickle
from User import User

#import imp
#from Node
#import Node
#newNode=
#imp.reload(Node)

from xml.dom import minidom

#This is a independent file and it will be executed from the front end to update the user and repo information to the data file
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

#node_dict={}

def loadPickleDictionary(path = None) :
    try :
        if(path is None):
            path = '/Users/Dany/Documents/gitnotus/framework/user_dict.pkl'
            with open(path, 'r') as pickle_in:
                dictionary = pickle.load(pickle_in)
                return dictionary
    except:
        #print 'Cannot open node_dict.pkl file'
        return None


def GetUserDict(path = None):
    dictionary=loadPickleDictionary(path)
    if dictionary is not None :
        return dictionary
    else :
        node_dict={}
        return node_dict

def update_dict(uname, repo_name, email):
    user_dict=GetUserDict()
    #user = user_dict[uname]
    user_dict[uname] = User(str(repo_name), str(email))
    with open('/Users/Dany/Documents/gitnotus/framework/user_dict.pkl','w') as user_pickle_out:
        pickle.dump(user_dict,user_pickle_out)
        #node_pickle_out.close()


def get_email_address(uname):
    user_dict=GetUserDict()
    user = user_dict[uname]
    if user == None:
        return None
    else:
        return user.email_address

def is_repo_available_returnmail(repo_name):
    user_dict=GetUserDict()
    for user in user_dict:
        user_obj = user_dict[user]
        if user_obj.repo_name == repo_name:
            return user_obj.email_address
        else:
            return None

    user = user_dict[uname]
    if user == None:
        return None
    else:
        return user.email_address


if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    update_dict('dineshappavoo', 'labineer', 'dinesha.utd@gmail.com')
    user_dict = GetUserDict()
    print user_dict
    print get_email_address('dineshappavoo')
    print is_repo_available_returnmail('gitnotus')

