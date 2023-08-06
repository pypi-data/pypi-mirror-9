LINE
----


**2014.08.08** Announcement: some codes are removed because of the
request of LINE corporation. You can use library only with ``authToken``
login.

The documentation is available at
`here <http://carpedm20.github.io/line/>`__

*May the LINE be with you...*


Update
------

**2015.03.31**

A well-known problem (`issue`_)of 2 hours authToken expiration that
shows ``code= 8 reason='EXPIRED'`` error is finally SOLVED!

You don’t have to change your code because the new code automatically
catch the expiration and update the authToken.

But, you can manually update your authToken by:

::

    from line import LineClient, LineGroup, LineContact
    client = LineClient("ID", "PASSWORD")
    client.updateAuthToken() # manual update

**2014.08.08**

Some codes are removed because of the request of LINE corporation. You
can use library only with ``authToken`` login.

.. _issue: https://github.com/carpedm20/LINE/issues/9

Screenshot
----------

.. figure:: http://3.bp.blogspot.com/-FX3ONLEKBBY/U9xJD8JkJbI/AAAAAAAAF2Q/1E7VXOkvYAI/s1600/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA+2014-08-02+%E1%84%8B%E1%85%A9%E1%84%8C%E1%85%A5%E1%86%AB+10.47.15.png
   :alt: alt\_tag

Author
------

Taehoon Kim / [@carpedm20](http://carpedm20.github.io/about/)

.. |PyPi version| image:: https://pypip.in/v/line/badge.png?style=flat
   :target: https://pypi.python.org/pypi/line
.. |PyPi downloads| image:: https://pypip.in/d/line/badge.png?style=flat
   :target: https://pypi.python.org/pypi/line
.. |PyPi status| image:: https://pypip.in/status/line/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/line
.. |PyPi license| image:: https://pypip.in/license/line/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/line

