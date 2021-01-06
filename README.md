#Dependencies
-python3.6

#Installation Instructions:
(this is tested on a desktop running ubuntu 16.04 with a 1080 ti gpu)
-generate secret key and put in line 7 of './flaskr/__init__.py'
-make virtual env 'python3.6 -m venv ./webdemoVenv36'
-install python packages below
-make symbolic links in /flaskr/static/
    'ln -s ../../uploaded_ims/ ./'
    'ln -s ../../output_ims/ ./'

#Python Package Dependencies
-torch 1.5 for cuda 9.2
-imageio
-numpy
-flask
-celery
-waitress


#Startup Instructions:
In terminal window/ screen/ tmux session #1:
'''
source webdemoVenv36/bin/activate
waitress-serve --call 'flaskr:create_app'
'''

In terminal window/ screen/ tmux session #2:
'''
source webdemoVenv36/bin/activate
celery -A flaskr worker --loglevel=INFO
'''

The webdemo should now be served on port 8080. If you want to forward port 80
to 8080 (for a nicer web address), see here: 
https://askubuntu.com/questions/444729/redirect-port-80-to-8080-and-make-it-work-on-local-machine





