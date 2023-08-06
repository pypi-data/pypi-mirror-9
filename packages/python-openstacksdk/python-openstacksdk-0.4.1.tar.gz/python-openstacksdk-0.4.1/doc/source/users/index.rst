Getting started with the OpenStack SDK
======================================

For a listing of terms used throughout the SDK, including the names of
projects and services supported by it, see the `Glossary <glossary>`_.

Installation
------------

The OpenStack SDK is available on
`PyPI <https://pypi.python.org/pypi/python-openstacksdk>`_ under the name
**python-openstacksdk**. To install it, use ``pip``::

   $ pip install python-openstacksdk

User Guides
-----------

These guides walk you through how to make use of the libraries we provide
to work with each OpenStack service. If you're looking for a cookbook
approach, this is where you'll want to begin.

.. toctree::
   :maxdepth: 1

   Connecting to an OpenStack Cloud <userguides/usage>
   Working with data in the Object Store <userguides/object_store>

API Documentation
-----------------

Service APIs are exposed through a two-layered approach. The classes
exposed through our *Connection* interface are the place to start if you're
an application developer consuming an OpenStack cloud. The *Resource*
interface is the layer upon which the *Connection* is built, with
*Connection* methods accepting and returning *Resource* objects.

Connection Interface
********************

A *Connection* instance maintains your session, authentication, transport,
and preferences, providing you with a set of higher-level interfaces to work
with OpenStack services.

.. toctree::
   :maxdepth: 1

   connection
   user_preference

Once you have a *Connection* instance, the following services may be exposed
to you. Your user preferences determine the full set of exposed services,
but listed below are the ones provided by this SDK by default.

.. toctree::
   :maxdepth: 1

   Object Store <proxies/object_store>

Resource Interface
******************

The *Resource* layer is a lower-level interface to communicate with OpenStack
services. While the classes exposed by the *Connection* build a convenience
layer on top of this, *Resources* can be used directly. However, the most
common usage of this layer is in receiving an object from a class in the
*Connection* layer, modifying it, and sending it back into the *Connection*
layer, such as to update a resource on the server.

The following services have exposed *Resource* classes.

.. toctree::
   :maxdepth: 1

   Compute <resources/compute/index>
   Database <resources/database/index>
   Network <resources/network/index>
   Object Store <resources/object_store/index>
   Volume <resources/volume/index>

Low-Level Classes
*****************

The following classes are not commonly used by application developers,
but are used to construct applications to talk to OpenStack APIs. Typically
these parts are managed through the `Connection Interface`_, but their use
can be customized.

.. toctree::
   :maxdepth: 1

   session
   transport
   base_auth_plugin
   identity_base
   identity_v2
   identity_v3
   resource
   service_filter
   utils
