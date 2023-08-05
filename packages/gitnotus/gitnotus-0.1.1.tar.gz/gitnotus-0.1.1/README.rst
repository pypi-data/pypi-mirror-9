gitnotus : github notification
====================================

.. image:: https://drone.io/github.com/dineshappavoo/gitnotus/status.png
   :target: https://drone.io/github.com/dineshappavoo/gitnotus
   :alt: drone.io CI build status

.. image:: https://pypip.in/v/gitnotus/badge.png
   :target: https://pypi.python.org/pypi/gitnotus/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/gitnotus/badge.png
   :target: https://pypi.python.org/pypi/gitnotus/
   :alt: Number of PyPI downloads

`gitnotus` is a set of API's/tools written to manage github events. Event updates will be notified through web hooks.

Configuration
==============
- Make apache tomcat web server up and running
- Make an public URl to post the hook
- In local use ngrok.com to make an URL. Next two steps are required in case if you do not have an public domain
- download and install ngrok
- ./ngrok 8080
- Add the webhook URL to the git repo
- Start the webhook_handler to recieve json ./weghook_handler.py
- Start the local smtp server on port 1025 using the following command 'python -m smtpd -n -c DebuggingServer localhost:1025' to send emails 

Features
========
* CLI to manage and effetively utilize github events.

Requirements
============
* Python 2.6, 2.7, 3.2, 3.3, 3.4
* Flask
* json
* pickle

License
=======
MIT
