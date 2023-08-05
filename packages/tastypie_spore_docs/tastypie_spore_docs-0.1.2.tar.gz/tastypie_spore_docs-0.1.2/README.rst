tastypie_spore_docs
======

This is tastypie_spore_docs package developed at Chembl group, EMBL-EBI, Cambridge, UK.

This package generates live online documentation as a SPORE client from the tastypie REST endpoint.

Rationale?
--------

Imagine you have just finished your `Tastypie-based <https://django-tastypie.readthedocs.org/en/latest/>`_
`REST <https://en.wikipedia.org/wiki/Representational_state_transfer>`_
`API <https://en.wikipedia.org/wiki/Application_programming_interface>`_.
You would probably like to encourage some developers to use it.
But how to do it without documentation?
Documentation is important but it's also boring to write.
And since people will read the documentation online, from their browsers they could execute your REST API as well.


This library solves all your problems - it generates live online documentation for you.
It can inspect your tastypie API, get all available methods and generate a nice online documentation, where everyone
can try them.
It does this by generating a `SPORE <https://github.com/SPORE/specifications>`_
endpoint and providing JavaScript-based client which consumes the
endpoint and renders documentation.

Setting it up
--------

As with every Django application, the first thing to do is to add it to ``INSTALLED_APPS`` list.::

      INSTALLED_APPS = (
          ...
          'tastypie_spore_docs',
          ...
      )

Apart from this, there is one required parameter that you have to include in your ``settings.py``.
It is called ``TASTYPIE_DOC_API`` and it should be a string containing a dotted path to your tastypie api instance.::

      TASTYPIE_DOC_API = 'path.to.rest.api'

There is another, optional parameter called ``TASTYPIE_DOC_NAME``, which will be a title on the documentation page.::

      TASTYPIE_DOC_NAME = 'My brand new documentation'

This application provides an url conf so you need to include it in your ``urls.py`` in order to see it.

Customising method required parameters and description
--------

Sometime your REST method requires more than one parameter or requires some custom description.
You can customise this by adding ``required_params`` and ``descriptions`` dictionaries to your tastypie resource ``Meta`` class.
For both dictionaries, the keys should be a method name (for example ``api_get_detail``).
The value is a list of parameter names (strings) for ``required_params`` and string with description for ``descriptions``.


Template Customisation
--------

This app provides two templates: ``docs.html`` and ``head_banner.html``.
``docs.html`` sets up a SPORE client and should be modified.
``head_banner.html`` adds custom content to the to of documentation and should be extended/overwritten.