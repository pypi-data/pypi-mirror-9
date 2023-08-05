============================
Pyramid Ziggurat Foundations 
============================

This template is a combination of Chameleon template engine and Ziggurat
Foundations user management. Usage::

    $ myenv/bin/pcreate -s ziggurat myproject
    $ cd myproject 
    $ myenv/bin/python setup.py develop-use-pip

Edit ``development.ini`` file for database auth then run::

    $ myenv/bin/initialize_myproject_db development.ini

Run web server::

    $ myenv/bin/pserve development.ini --reload

Open URL http://localhost:6543 in a browser. Login with username
``admin@local`` or ``admin``, password ``admin``.

