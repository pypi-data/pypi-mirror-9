django-websocket-redis
======================

Project home: https://github.com/jrief/django-websocket-redis

Detailed documentation on [ReadTheDocs](http://django-websocket-redis.readthedocs.org/en/latest/).

Online demo: http://websocket.aws.awesto.com/

Websockets for Django using Redis as message queue
--------------------------------------------------
This module implements websockets on top of Django without requiring any additional framework. For
messaging it uses the [Redis](http://redis.io/) datastore and in a production environment, it is
intended to work under [uWSGI](http://projects.unbit.it/uwsgi/) and behind [NGiNX](http://nginx.com/).

New in 0.4.2
------------
* Message echoing can be switched “on” and “off” according to the user needs. Before it was “on” by
  default.
* Many changes to become compatible with Python3; there are still minor issues to solve.
* The message string to be passed and stored to and from the websocket hase been converted into
  a class ``RedisMessage`` for type saftey.

Features
--------
* Largely scalable for Django applications with many hundreds of open websocket connections.
* Runs a seperate Django main loop in a cooperative concurrency model using [gevent](http://www.gevent.org/),
  thus only one thread/process is required to control *all* open websockets simultaneously.
* Full control over this seperate main loop during development, so **Django** can be started as usual with
  ``./manage.py runserver``.
* No dependency to any other asynchronous event driven framework, such as Tornado, Twisted or
  Socket.io/Node.js.
* Normal Django requests communicate with this seperate main loop through **Redis** which, by the way is a good
  replacement for memcached.
* Optionally persiting messages, allowing server reboots and client reconnections.

If unsure, if this proposed architecture is the correct approach on how to integrate Websockets with Django, then
please read Roberto De Ioris article about
[Offloading Websockets and Server-Sent Events AKA “Combine them with Django safely”](http://uwsgi-docs.readthedocs.org/en/latest/articles/OffloadingWebsocketsAndSSE.html).

Please also consider, that whichever alternative technology you use, you always need a message queue,
so that the Django application can “talk” to the browser. This is because the only link between the browser and
the server is through the Websocket and thus, by definition a long living connection. For scalability reasons you
can't start a Django server thread for each of these connections.

Build status
------------
[![Build Status](https://travis-ci.org/jrief/django-websocket-redis.png?branch=master)](https://travis-ci.org/jrief/django-websocket-redis)
[![Downloads](http://img.shields.io/pypi/dm/django-websocket-redis.svg?style=flat-square)](https://pypi.python.org/pypi/django-websocket-redis/)

Questions
---------
Please use the issue tracker to ask questions.

License
-------
Copyright &copy; 2015 Jacob Rief.

MIT licensed.
