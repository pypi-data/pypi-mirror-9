ripozo
======

A pluggable tool for quickly and efficiently creating web apis.
In the modern day, your server is no longer just interacting
with a web browser.  Instead it's interfacing with desktop and mobile 
web browsers, multiple native applications, and maybe even being exposed
as an API to other developers.  Ripozo is designed to solve this problem.
It allows you to easily build Hypermedia/HATEOAS/REST APIs quickly and 
efficiently.

Philosophy
----------

Hypermedia
^^^^^^^^^^

Ripozo is designed first and foremost behind the belief that Hypermedia
APIs are the way everything should be developed.  With hypermedia APIs and
good client consumers, boilerplate code is removed and a developer is free
to focus on making the difficult decisions and writing the business logic,
not the boiler plate code.  It should be noted that ripozo goes beyond
CRUD+L.  CRUD+L is a good step in the right direction, but it still requires
too much knowledge on the client side still.  With true Hypermedia, the 
client doesn't need to how to construct URLs or what the actions available
on a given resource are.  The server can simply tell you.

Unopinionated (unless you want it to be)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ripozo doesn't make design decisions for you.  Ripozo is a tool that is capable
of being used in any existing web framework.  It can be used with any database.
Any Hypermedia protocol can be used.  If you really wanted to, though we don't
recommend it, you could even render raw HTML with a tool like Jinja2.  You could
even theoretically skip the web application all together and use it directly instead
of through a web api. Long story short, Ripozo doesn't care how it is used.  
It can be plugged in for a small part of your application or used exclusively.

Extensible and Pluggable
^^^^^^^^^^^^^^^^^^^^^^^^

Ripozo is extensible/pluggable.  Just because ripozo itself doesn't make design decisions
for you doesn't mean that it shouldn't be batteries included, we just believe
that the batteries included versions should be split out into other packages.
Hence its extensibility.  There are already packages that make it easy to use
both Cassandra and SQL databases via cqlengine and SQLAlchemy.  There's an 
adaption of ripozo for integration with Flask.  We didn't want to make design
decisions for you.  But we figured that if you wanted something more opinionated,
we'd make it easy to extend ripozo.  As a side note, we really hope that you 
open source any ripozo based packages that you create and let us know.  After all,
let's keep our open source world DRY.

Basic Concepts
==============

Alright, so you're probably tired of hearing about all our self righteous talk 
about ripozo's philosophy and want to know how you can actually use it to start
building awesome APIs.  Ripozo has four basic pieces: Dispatchers, Adapters, Resources,
and Managers.  tl:dr; version: Dispatchers handle incoming requests and direct
them to Resources.  Resources perform the business logic, optionally using a 
Manager to interact with a database.  The Resource returns an instance of itself
to the dispatcher which determines which Adapter to use.  The adapter then takes the
Resource instance and formats it into an appropriate response.  The dispatcher then
returns this response.

Now for the more detailed descriptions...

Dispatchers
-----------

In this base ripozo package, the dispatcher is simply an abstract base class
with a few convience methods.  Since the handling of incoming requests is
dependent on the framework you are using, and we don't want to make design 
decisions for you, we thought that this would be a bad place for making opinionated
decisions.  However, the upside is that it is very easy to create dispatchers.
In fact, a Flask dispatcher has already been created and is only one file less than
100 lines long. In the future we will be adding more webframework specific 
dispatchers and plan on making a framework of our own that is specific to ripozo.

Resources
---------

Resources are the bread and butter of ripozo.  They determine the business logic
of an application.

Managers
--------

Managers are more or less the state keepers of the application.

Adapters
--------

Adapters determine the format in which to return a response.  They take a resource
instance and generate what the response should look like.  For example, you could 
have an adapter that returns a SIREN response and another adapter that returns a HAL
response.  The best part is, that these are entirely reusable.  That means that 
you can support as many adapters as are written by anyone in the world with no extra
work on your part outside of installing the extra adapter packages.  This is extemely 
useful because you can write your logic once and not have to worry about duplicating
your code so that the front-end web team can use SIREN and the mobile team can use
basic CRUD+L.