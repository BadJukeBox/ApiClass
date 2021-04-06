# ApiClass

###How to Use (With Docker):
``Docker build -t api-class .``

``docker run -it api-class:latest  /bin/sh``

``cd /usr/local/bin/api-class``

####For testing
``cd tests``

``py.test``

####For the main program
``cd src``

``python3 json_placeholder.py``

###Notes
There are a few changes I would make to this program if it were to be written for something production ready/a real service.
1. First I would include full CRUD functionality for both posts and comments.
2. The base RequestApi class would likely be in its own module.
3. I would likely expand the Exception handling a bit so that rather than returning None more/custom Exceptions are raised and handled in a main routine instead with logging.
