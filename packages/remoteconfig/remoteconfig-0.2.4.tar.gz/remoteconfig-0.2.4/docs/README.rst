remoteconfig
============

A simple wrapper for localconfig_ that allows for reading config from a remote server

Quick Start Tutorial
====================

To install::

    pip install remoteconfig

To read from a remote config:

.. code-block:: python

    from remoteconfig import config

    config.read('http://url/to/remote-config.ini')

    # Or cache the URL content for 60 seconds to avoid excessive download if program is invoked often
    # config.read('http://url/to/remote-config.ini', cache_duration=60)
    #
    # Or instantiate another config instance:
    # from remoteconfig import RemoteConfig
    # config2 = RemoteConfig('http://url/to/another-config.ini', cache_duration=10)

For everything else that you can do with `config`, refer to `localconfig's documentation`_

.. _localconfig: https://pypi.python.org/pypi/localconfig
.. _`localconfig's documentation`: http://localconfig.readthedocs.org


More
====

| Documentation: http://remoteconfig.readthedocs.org
|
| PyPI Package: https://pypi.python.org/pypi/remoteconfig
| GitHub Source: https://github.com/maxzheng/remoteconfig
| Report Issues/Bugs: https://github.com/maxzheng/remoteconfig/issues
|
| Connect: https://www.linkedin.com/in/maxzheng
| Contact: maxzheng.os @t gmail.com
