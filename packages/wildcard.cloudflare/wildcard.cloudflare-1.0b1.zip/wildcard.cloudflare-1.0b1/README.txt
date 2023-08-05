Introduction
============

.. image:: https://www.wildcardcorp.com/logo.png
   :height: 50
   :width: 382
   :alt: Original work by wildcardcorp.com
   :align: right


This is a very simple package to integrate the Content Delivery Network (CDN) CloudFlare into the ability to do cache purging
with plone.app.caching. 


Usage
-----

- Install "CloudFlare Cache Purging" addon
- Go to "Caching" control panel and make sure "Enable purging" is checked
  in the "Caching proxies" tab.
- Make sure to also configure which content types to enable purging on and
  make sure to check if you are using virtual host urls
- Go to the "CloudFlare" control panel and fill in settings
- Make test purge requests


Tested with Plone 4.3.x
