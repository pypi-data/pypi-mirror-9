.. image:: https://travis-ci.org/benemery/filewatch.svg?branch=master
    :target: https://travis-ci.org/benemery/filewatch

.. image:: https://coveralls.io/repos/benemery/filewatch/badge.svg?branch=master&foo=bar
  :target: https://coveralls.io/r/benemery/filewatch?branch=master



FILEWATCH
=========

Keep track of what files change and when with this super easy to use package.

Installation
------------

Install using pip:

.. code-block:: console

    $ pip install filewatch

Then create and register your observer:

.. code-block:: python

    # your_observer.py
    from filewatch import ObserverBase, file_updated_subject, Watcher

    class YourObserver(ObserverBase):
        def notify(self, *args, **kwargs):
            file_list = kwargs['file_list']
            print 'These files have been updated %s' % file_list

    file_updated_subject.register_observer(YourObserver())
    watcher = Watcher()
    watcher.run()

Then simply execute the file:

.. code-block:: console

    $ python your_observer.py

Now every time that a file is created / modified within your current working
directory, the system will print to console which file was updated.
