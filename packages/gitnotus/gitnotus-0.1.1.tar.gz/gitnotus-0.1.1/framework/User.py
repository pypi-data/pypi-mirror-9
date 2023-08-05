#!/usr/bin/python

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

#Node object/class to maintain the hardware information
class User:
    'Common base class for all Users'
    usercount = 0
    
    def __init__(self, repo_name, email_address):
        self.repo_name = repo_name
        self.email_address = email_address
