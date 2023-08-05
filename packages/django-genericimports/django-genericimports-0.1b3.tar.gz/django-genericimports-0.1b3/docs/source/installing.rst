Installing
==========

Installing genericimports stable
--------------------------------

Installing django-genericimports is easy, just type in:

::

    $ pip install django-genericimports

It will take care of installing almost all the dependencies for you.

Installing a genericimports development version
----------------------------------------------

To be written...

Embedding in your project
-------------------------

I'm usually against embedding third party applications in projects for a good
number of reasons, yet there are small situations where you want to do it.

To embed the application in your project should be more complex than copying
the folder "genericimports" to your project as a new application, and adding
the applications listed in the "install_requires" in the setup.py file to
your requirements file (if you have one. If you don't... you should have it)

Apart from that the rest is exactly the same, the only thing that you have to
care about is the import path. You won't be able to use "genericimports"
straight in again, rather you will have to put your own module path,
something along the lines of "myapps.genericimports"

Installing Redis
----------------

One of the requirements of the current version of django-genericimports is to
have redis available on the server, or to have a remote redis instance that
can be used.

In most of the cases you won't have one, but don't run away, you only need to
install it and run the redis service, django-rq will take care of the rest.

To install redis in ArchLinux::

    $ sudo pacman -S redis
    $ sudo systemctl enable redis

To install redis on Debian/Ubuntu::

    $ sudo apt-get install redis-server python-redis
    $ update-rc.d redis defaults
