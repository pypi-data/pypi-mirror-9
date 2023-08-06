================
cmsplugin-polls
================

|ci| |pypi| |status|

.. |ci| image:: https://travis-ci.org/satyrius/cmsplugin-polls.png?branch=master
    :target: https://travis-ci.org/satyrius/cmsplugin-polls

.. |pypi| image:: https://pypip.in/version/cmsplugin-polls/badge.png?text=pypi
    :target: https://pypi.python.org/pypi/cmsplugin-polls/
    :alt: Latest Version

.. |status| image:: https://pypip.in/status/cmsplugin-polls/badge.png
    :target: https://pypi.python.org/pypi/cmsplugin-polls/
    :alt: Development Status

Why?
====
There is no established Polls plugin for DjangoCMS. Yes, `cmsplugin-poll <https://bitbucket.org/tonioo/cmsplugin-poll>`_ exists, 
but it's latest update was at 2013 and looks like it is abandoned. Personaly I want a simple plugin, that is up to date and support
latest Django and DjangoCMS. So this one could be at the spot.

Requirements
============

It works fine and tested under ``Python 2.7``. The following libraries are required

- ``Django`` >= 1.5
- ``django-cms`` >= 3.0 (we recommend to use Django CMS 3.0 and higher, contact us if you need prior CMS versions supports and have some issues)

Installation
============
::

  $ pip install cmsplugin-polls

Update your ``settings.py`` ::

  INSTALLED_APPS = [
      # django contrib and django cms apps
      'cmsplugin_polls',
  ]

Do not forget to include URLs to ``urls.py`` (namespace is important) ::

  urlpatterns = patterns('',
      url(r'^polls/', include('cmsplugin_polls.urls', namespace='polls')),
      url(r'^', include('cms.urls')),
  )

And to migrate your database ::

  django-admin.py migrate captcha cmsplugin_polls

Roadmap
=======
- AJAX submiting out-of-box
- Python 3 support

Contributing
============
Fork the repo, create a feature branch then send me pull request. Feel free to create new issues or contact me via email.

Translation
-----------
You could also help me to translate `cmsplugin-polls` to your native language `with Transifex <https://www.transifex.com/projects/p/cmsplugin-polls/resource/main/>`_

