#!/usr/bin/env python

from flask import Flask, render_template
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