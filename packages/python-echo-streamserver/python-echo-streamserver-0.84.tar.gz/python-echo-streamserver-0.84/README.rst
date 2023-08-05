=====================
Echo StreamServer API
=====================

This is a Python version of the **Echo StreamServer API**. See the Echo Developers_ Documentation.

Function Interface
==================

The *function* interface provides each **API** as a simple *module* or *package*. The **API** uses the **Default Account** to contact **Echo**. For example, the **Items API** is **echo.items** and has the **REST API** methods.

>>> # Items API: Count EQL Query
>>> from echo import items, StreamServerError
>>> try:
>>>     n = items.count("scope:http//example.com/\*")
>>>     print "EQL Count: %d" % n
>>> except StreamServerError, e:
>>>     print "Error: %s" % str(e)

Default Account
---------------

The **Default Account** is part of the **echo.settings** module. Set the **Echo** *appkey* and *secret* API_Keys there.

::
    /usr/lib/python2.x/site-packages/echo/settings.py

Client Interface
================

The **Client** interface provides each **API** as a class *instance*. The **Client** uses an **Account** object to contact **Echo**, or the default. For example, the **Key-Value Store API** is **echo.kvs.Client** and has the **KVS API** methods.

>>> # KVS Client API: Get a value for the key 'sample'.
>>> from echo import kvs, StreamServerError
>>> # Create a KVS client using the default account.
>>> client = kvs.Client()
>>> try:
>>>     v = client.get('sample')
>>>     print "KVS: %r" % v
>>> except StreamServerError, e:
>>>     print "Error: %s" % str(e)

Account Objects
===============

Each **Client** *instance* can use an **Account** object to contact **Echo**. This is required to support *multiple* **Echo** accounts.

>>> from echo import feeds, Account
>>> # Non-default account: Login Account.BasicAuth with no secret
>>> other_account = Account('test.echoenabled.com', '', Account.BasicAuth)
>>> client = feeds.Client(account=other_account)

MUX Requests
============

The **Items API** supports **MUX**, or *multiplexed* requests. Several **count** and **search** requests can be combined into one **REST** call. The **items.mux** method sends a list of **MuxRequest** objects to **Echo**. See the **Echo** mux_ method documentation for the output format.

>>> from echo import items
>>> from echo.items.mux_api import MuxRequest
>>> # EQL Query String
>>> query_eql = "scope:http://www.example.com/\*"
>>> # Search Query (default)
>>> search = MuxRequest(query_eql)
>>> # Count Query
>>> count = MuxRequest(query_eql, api_method='count')
>>> # Form list of them for Mux API.
>>> requests = [ search, count ]
>>> # Send Mux API requests.
>>> r = items.mux(requests)

Echo Query Language Builder
===========================

There is an *object-oriented* **Echo Query Language API** to build query strings. An **echo.eql.Query** object may be passed to the **Items API** methods **eql.items.count** and **eql.items.search** rather than query text. Add **echo.eql.filters** to build on the query terms and produce a complete EQL_ query string.

EQL Syntax Limitations
----------------------

This **EQL Builder** *does not guarantee* that the *whole* EQL text is valid. Each *term* is valid alone but **Echo StreamServer** still may reject the EQL string. **EQL syntax** rules limit how a **Query** and its **filters** can be constructed. Print the **echo.eql.Query** object to inspect its query string and *reorder* filter terms as necessary.

Query Method API
----------------

Build an **echo.eql.Query** object using method calls. Add **echo.eql.filters.QueryFilter** objects to limit the results. Most **QueryFilter** objects can be *negated* to exclude the term.

>>> from echo import eql
>>> q = eql.Query("http://site.example.com/index.html", uri_filter='url')
>>> q.add_filter(eql.filters.ChildrenDepth(3))
>>> q.add_filter(eql.filters.TypeFilter('article'), negate=True)
>>> print "EQL> ", q
EQL> "url:"http://site.example.com/index.html" children:3 -type:article"

Query Operator API
------------------

Add *filters* to an **echo.eql.Query** object using boolean operators. Read the **echo.eql.filters** documentation for more details.

>>> from echo import eql
>>> q = eql.Query("http://www.example.com/movies//")
>>> # Exclude articles and notes with (-).
>>> q = q - eql.filters.TypeFilter(['article', 'note'])
>>> # Allow children up to depth 2.
>>> q + (eql.filters.ChildrenDepth(2))

========  =======  ===========
echo.eql.Query Operators
------------------------------
operator  example  description
========  =======  ===========
plus +    q + r    **Add** filter r to query q.
minus -   q - r    **Negate** filter r on query q.
and &     q1 & q2  Combine queries q1 **and** q2.
pipe |    q1 | q2  Select query q1 **or** q2.
========  =======  ===========

========  =======  ===========
echo.eql.filters Operators
------------------------------
operator  example  description
========  =======  ===========
minus -   -r       **Negate** filter r.
and &     r1 & r2  Combine filters r1 **and** r2.
pipe |    r1 | r2  Apply filter r1 **or** r2.
========  =======  ===========

.. _Developers: http://echoplatform.com/streamserver/docs/rest-api/
.. _mux: http://echoplatform.com/streamserver/docs/rest-api/other-api/mux/
.. _EQL: http://echoplatform.com/streamserver/docs/features/echo-query-language/

