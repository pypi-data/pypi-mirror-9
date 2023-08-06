Introduction
============

This package adds Site-Wide Notification/Status Messages for Plone CMS.

This package adds
-----------------

* control panel where site administrator could add new notice, edit/delete
  existing notices
* viewlet which will insert notices, or multiple notices into plone page

Notice Fields
-------------

* Required: rich html 'Body' text (with TinyMCE editor)
* Optional: 'Display To' field where admin could pick list of users and/or
  groups to display notice to, if not set then notice is displayed to everybody
* Optional: 'Period' field which includes: Effective and Expiration datetimes
  with nice calendar/time widgets; if left empty, then notice is displayed to a
  user until he/she closes it

Notices Viewlet
---------------

This viewlet displays each notice with close button, so user can close it. This
action is remembered in a cookie so after page reload notice doesn't show up.
Also we can have multiple notices for the same user. If notice has set period
field, then notice disappears automatically after Expiration date.
