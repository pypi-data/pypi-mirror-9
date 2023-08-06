========
ServConn
========

---------------------------------
Connection-less Access to Servers
---------------------------------

Introduction
============

Usually when dealing with connecting to servers, you need to keep track of various objects and use similar syntax everywhere in your code. This package exists to minimize the amount of redundancy in server connections by abstracting connections through objects. The currently implemented wrappers include:

DatabaseConnector
    A class that wraps connections to MySQL

SocketConnector
    A class that wraps connections to servers via sockets

Installation
============

To install this package, either download the project from Pypi or simply run ``pip install servconn``.

Documentation
=============

View the README file for documentation, or view the online documentation `here <http://brandonchinn178.github.io/servconn>`_.