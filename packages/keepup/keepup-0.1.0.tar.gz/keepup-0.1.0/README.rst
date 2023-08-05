**********************************
keepup
**********************************

keepup is a command line process manager, similar to `Foreman <https://github.com/ddollar/foreman>`_ and `Honcho <https://github.com/nickstenning/honcho>`_, except it uses `npyscreen <https://code.google.com/p/npyscreen/>`_ to provide a curses interface for monitoring stdout, stderr, and for sending input to stdin.

keepup uses an ``Upfile`` similar to a ``Procfile``. An example is shown below

.. code-block:: python

  # Upfiles support comments by prefixing a line with the # character
  mytask: python myscript.py
  # The following line will set the working directory for the specified task
  @mytask: /home/user/directory

Support for advanced features is limited.