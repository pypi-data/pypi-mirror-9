Django Rest Framework-Angular Authorization
===================


## Installation
Install the package

 
```bash
    $ pip install drf_authentication
    $ python manage.py bower_install
```
You must add 'bower' and 'drf_authentication' to INSTALLED_APPS.


## Dependencies
    
    django
    djangorestframework
    jack_bower



## Demo
[Demo ](https://drf-auth-angular.herokuapp.com/) you can check it out.

##Testing


Run all tests:
```bash
    $ tox
```

Start test with nose and code coverage:
```bash
    $ nosetests --with-cov  --cov-report html  --cov  drf_angular_auth tests/
```


