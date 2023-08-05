==================
kotti_link
==================

|pypi|_
|downloads_month|_
|license|_
|build status|_

.. |pypi| image:: https://img.shields.io/pypi/v/kotti_link.svg?style=flat-square
.. _pypi: https://pypi.python.org/pypi/kotti_link/

.. |downloads_month| image:: https://img.shields.io/pypi/dm/kotti_link.svg?style=flat-square
.. _downloads_month: https://pypi.python.org/pypi/kotti_link/

.. |license| image:: https://img.shields.io/pypi/l/kotti_link.svg?style=flat-square
.. _license: http://www.repoze.org/LICENSE.txt

.. |build status| image:: https://img.shields.io/travis/j23d/kotti_link/master.svg?style=flat-square
.. _build status: http://travis-ci.org/j23d/kotti_link

Link content type for Kotti.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_link`` add-on in your Kotti site, you need to
add an entry to the ``kotti.configurators`` setting in your Paste
Deploy config.  If you don't have a ``kotti.configurators`` option,
add one.  The line in your ``[app:main]`` (or ``[app:kotti]``, depending on how
you setup Fanstatic) section could then look like this::

    kotti.configurators = kotti_link.kotti_configure

``kotti_link`` extends your Kotti site with a link content type that allows you to
add a document with the capability to link to any other place in the internal site
or anywhere in the internet. You have to specify the link in the edit mode of the
link content type to the attribute link. Internal redirects should start with ``/``
and external with ``http://``. Then you have to adjust the default view for your
object to ``Redirect View``.

.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
