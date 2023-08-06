helga-wiki-whois
================

A command plugin to generate a confluence-type URL for a user, assuming that the nick given
is a valid confluence user. If given a nick 'foo', the end result this command produces is
something like ``http://example.com/~foo``. Usage::

    helga (showme|whois|whothehellis) <nick>


Settings
--------

**WIKI_URL** Formattable WIKI url containing the substring named {user} (i.e. http://example.com/~{user})


License
-------

Copyright (c) 2015 Shaun Duncan

Licensed under an `MIT`_ license.

.. _`MIT`: https://github.com/shaunduncan/helga-wiki-whois/blob/master/LICENSE
