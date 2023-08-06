Extensions
==========

Welcome to the Eve extensions registry. Here you can find a list of packages
that extend Eve. This list is moderated and updated on a regular basis. If you
wrote a package for Eve and want it to show up here, just `get in touch`_ and
show me your tool! 

- Eve-Elastic_
- Eve-Mongoengine_
- Eve-Docs_
- Eve-Mocker_
- Eve.NET_
- Eve-SQLAlchemy_
- Eve-OAuth2_ and Flask-Sentinel_

Eve-Elastic
-----------

| *by Petr Jašek*

Eve-Elastic_ is an elasticsearch data layer for the Eve REST framework.
Features facets support and the generation of mapping for schema. 

Eve-Mongoengine
---------------

| *by Stanislav Heller*

Eve-Mongoengine_ is an Eve extension, which enables Mongoengine ORM models to
be used as eve schema. If you use mongoengine in your application and
simultaneously want to use Eve, instead of writing schema again in Cerberus
format (DRY!), you can use this extension, which takes your mongoengine models
and auto-transforms them into Cerberus schema under the hood. 

Eve-Docs
--------

| *by Charles Flynn*

Eve-docs_ is a blueprint that generates documentation for Eve APIs in HTML and
JSON formats. Eve-docs creates the documentation from your existing Eve
configuration file, with no additional configuration required. For a nice
screenshot, check out the relevant blog post `Auto generate API docs`_.

Eve-Mocker
----------
*by Thomas Sileo*

`Eve-Mocker`_ is a mocking tool for Eve powered REST APIs, based on the
excellent HTTPretty, aimed to be used in your unit tests, when you rely on an
Eve API. Eve-Mocker has been featured on the Eve blog: `Mocking tool for Eve
APIs`_

Eve.NET
-------
*by Nicola Iarocci*

`Eve.NET`_ is a simple HTTP and REST client for Web Services powered by the Eve
Framework. It leverages both ``System.Net.HttpClient`` and ``Json.NET`` to
provide the best possible Eve experience on the .NET platform. Written and
maintained by the same author of the Eve Framework itself, Eve.NET is delivered
as a portable library (PCL) and runs seamlessly on .NET4, Mono, Xamarin.iOS,
Xamarin.Android, Windows Phone 8 and Windows 8. We use Eve.NET internally to
power our iOS, Web and Windows applications.

Eve-SQLAlchemy
--------------
*by Andrew Mleczko et al.*

Powered by Eve, SQLAlchemy and good intentions Eve-SQLALchemy_ allows to
effortlessly build and deploy highly customizable, fully featured RESTful Web
Services with SQL-based backends.

Eve-OAuth2
----------
*by Nicola Iarocci*

Eve-OAuth2_ is not an extension per-se, but rather an example of how you can
leverage Flask-Sentinel_  to protect your API endpoints with OAuth2. 

.. _`Mocking tool for Eve APIs`: http://blog.python-eve.org/eve-mocker
.. _`Auto generate API docs`: http://blog.python-eve.org/eve-docs
.. _charlesflynn/eve-docs: https://github.com/charlesflynn/eve-docs
.. _eve-mocker: https://github.com/tsileo/eve-mocker
.. _Eve-docs: https://github.com/charlesflynn/eve-docs
.. _`get in touch`: mailto:eve@nicolaiarocci.com
.. _Eve-Mongoengine: https://github.com/hellerstanislav/eve-mongoengine
.. _Eve-Elastic: https://github.com/petrjasek/eve-elastic
.. _Eve.NET: https://github.com/nicolaiarocci/Eve.NET
.. _Eve-SQLAlchemy: https://github.com/RedTurtle/eve-sqlalchemy
.. _Eve-OAuth2: https://github.com/nicolaiarocci/eve-oauth2
.. _Flask-Sentinel: https://github.com/nicolaiarocci/flask-sentinel
