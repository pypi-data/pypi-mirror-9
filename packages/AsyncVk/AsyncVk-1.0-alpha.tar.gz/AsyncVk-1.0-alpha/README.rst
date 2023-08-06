=========================
vk.com API async Python wrapper
=========================

AsyncVk project is a fork of pretty library 'vk' (https://github.com/dimka665/vk) by Dmitry Voronin (https://github.com/dimka665)

This is a vk.com (the largest Russian social network) async python API wrapper.
The goal is to support all API methods (current and future)
that can be accessed from server.

Quickstart
==========

Install
-------

.. code:: bash

    pip install AsyncVk

Usage
-----

.. code:: python

    >>> import asyncio
    >>> import AsyncVk
    >>>
    >>> @asyncio.coroutine
    >>> def some_method():
    >>>     vkapi = AsyncVk.API()
    >>>     # vkapi = AsyncVk.API(user_login='user@gmail.com', user_password='******', app_id='123456')
    >>>     # vkapi = AsyncVk.API(access_token='********************')
    >>>     time = yield from vkapi.getServerTime()
    >>>     print(time)
    >>>
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(some_method())
    >>> loop.close()


See https://vk.com/dev/methods for detailed API guide.

More info
=========

`Read full documentation <http://asyncvk.readthedocs.org>`_
