#!/usr/bin/env python

from flask import Flask, render_template

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

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/my-link/')
def my_link():
    print 'I got clicked!'
    return "OK"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)