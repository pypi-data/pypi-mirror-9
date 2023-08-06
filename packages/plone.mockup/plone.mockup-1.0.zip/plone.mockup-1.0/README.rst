plone.mockup
============

This is the integration package of ``mockup`` for Plone. Basically, it packages
``mockup`` as a Python egg. For mockup itself, see
https://github.com/plone/mockup

This package uses the ``git submodule`` feature. If you use
``buildout.coredev``, ``mr.developer`` will make sure that the submodule is
checked out properly. If you do it manually, you can do one of the following::

    $ git clone git@github.com/plone/mockup.git --recursive

or::
    
    $ git clone git@github.com/plone/mockup.git
    $ cd mockup
    $ git submodule update --init --recursive

.. note::
    Please, don't develop mockup in here. git submodules are known to be
    cumbersome in some circumstances. Do your mockup development directly in a
    separate, dedicated mockup checkout.
