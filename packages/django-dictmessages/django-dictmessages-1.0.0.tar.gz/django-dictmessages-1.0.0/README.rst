Django dictmessages
================

A small Django package allowing a dictionary to be passed to contrib.messages.
The dictionary is then pre-rendered and passed to the real contrib.message
function.



Dependencies
------------

A recent version of Django is required, but there are no third-party
dependencies for this package.


Installation
------------

Use your favorite Python installer to install it from PyPI::

    $ pip install django-dictmessages


Or get the source from the application site::

    $ hg clone https://bitbucket.org/mhurt/django-dictmessages
    $ cd django-dictmessages
    $ python setup.py install


Configuration
-------------

Add ``'dictmessages'`` to your ``INSTALLED_APPS`` setting like this::

    INSTALLED_APPS = {
      ...
      'dictmessages',
    }


Getting Started
---------------

Wherever you would normally make use of the ``django.contrib.messages`` API you
can use this package instead::

    # Before...
    from django.contrib import messages

    # After...
    from dictmessages import messages

Since ``dictmessages`` is a simply a wrapper around the original functionality,
you can continue to use it in the same way::

    from dictmessages import messages
    ...
    ...

    # This still works the same...
    messages.success(request, 'Awesome! You totally nailed that, dude.')


But, if you'd like to something a little more fancy...::

    from dictmessages import messages
    ...
    ...

    message_dictionary = dict(
        object='Awesome!', activity='You totally nailed that, dude.')

    messages.success(requestion, message_dictionary)
