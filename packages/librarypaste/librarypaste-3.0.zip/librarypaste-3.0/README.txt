A Python paste bin.

Install using ``pip install librarypaste`` and launch with the ``librarypaste``
command or with ``python -m librarypaste``. The library will host the service
on ``[::0]:8080`` by default. Pass cherrypy config files on the command line
to customize behaivor.

By default, the server saves pastes to the file system  in ``./repo`` using the
JSON store, but there is support for a MongoDB backend as well.

See also `lpaste <https://pypi.python.org/pypi/lpaste>`_ for a Python-based
client (including a clipboard helper) and Mac OS X App.
