helga-reviewboard
=================

A helga plugin for expanding shortcodes for code reviews on ReviewBoard. This matches the pattern
``cr(\d+)`` and requires configuring the setting ``REVIEWBOARD_URL``. For example::

    <sduncan> can someone look at cr1234
    <helga> sduncan might be talking about codereview: http://example.com/r/1234

This match plugin will also show links for any code review match it finds::

    <sduncan> can someone look at cr1234 and cr456
    <helga> sduncan might be talking about codereview: http://example.com/r/1234, http://example.com/r/456


Settings
--------

``REVIEWBOARD_URL``
    A URL string format for showing ReviewBoard links. This should contain a format parameter
    '{review}'. (default: 'http://localhost/{review}')


License
-------

Copyright (c) 2015 Shaun Duncan

Licensed under an `MIT`_ license.

.. _`MIT`: https://github.com/shaunduncan/helga-reviewboard/blob/master/LICENSE
