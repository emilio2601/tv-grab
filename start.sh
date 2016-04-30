#/bin/bash

source flask/bin/activate
flask/bin/python app.py &
flask/bin/python scheduler.py &
