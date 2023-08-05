pp.core - Produce & Publish Foundation
======================================

``pp.core`` implements some core foundation functionalities
of the Produce & Publish framework.

Provided functionality
----------------------

- filesystem abstraction
- integration with Dropbox and other cloud file services
- resource base
- resources registry
- filesystem registry  

Internals
---------

This module abstracts Produce & Publish basic functionality in order to make
the core implementation as re-usable as possible.  It uses the ``pyfilesystem``
to abstract arbitrary file operations independent of the underlaying storage
layer. Through this approach we are able to support local filesystems, network
filesystems or cloud storages like Dropbox without changing the application.
All storage subsystems can be accessed using the same API.

Requirements
------------

- Python 2.7 

For using the Dropbox storage API of ``pp.core`` you need to have ``Phantomjs``
installed (the ``phantomjs`` binary must be available in the ``$PATH``. PhantomJS
is required to fake the OAuth process of Dropbox.

Source code
-----------

https://bitbucket.org/ajung/pp.core

Bug tracker
-----------

https://bitbucket.org/ajung/pp.core/issues

Support
-------

Support for Produce & Publish Server is currently only available on a project
basis.

License
-------
``pp.core`` is published under the GNU Public License V2 (GPL 2).

Contact
-------

| Andreas Jung/ZOPYX 
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com
