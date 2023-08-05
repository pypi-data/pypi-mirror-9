About
============

Extension for Plone which adds new content view tab to all common content where Manager
can manage marker interfaces on instance level. Yep, in general this is just Plone UI
for "Interfaces" tab available in the ZMI.

Installing
============

This package requires Plone 3.x or later.

To install the package just add collective.interfaces into your eggs option of your
buildout main or instance section.

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Usage
============

There is new tab in the content views named "Interfaces" where you can see which
interfaces are provided by content's class and assign other available marker interfaces
to the object's instance.

Licence
============

collective.interfaces is licensed under the GPL. See LICENSE.txt for details.

