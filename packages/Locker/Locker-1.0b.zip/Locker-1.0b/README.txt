Hierarchical Resource Locking System
====================================

Locker exists to allow the coordination of resource locks across independent or distributed systems.
Systems utilizing Locker could be simple scripts, CI jobs or even separate network nodes, they only
need to be able to query the Locker instance via HTTP.

Locker is different from a standard sephemore system in that it understands resources as a
hierarchy. Resources are nested in the url path ie: "/foo/bar" where "bar" is a child of "foo".
If a lock exists on "/foo/bar" the parent ("/foo") cannot be locked because one of its children is
locked. Likewise a child of "/foo/bar" such as "/foo/bar/baz" cannot be locked because its parent
is locked. A sibling such as "/foo/zip" could be locked.

Resource names are completely arbitrary and not mapped to any physical resources. The systems
querying Locker are trusted not to utilize locked resources and to free resources when they are no
longer needed.


Initialization
--------------

Locker can be initialized by running the __init__.py in the Locker directory directly. This will
initialize Locker with an HTTP server on the default IP and port (127.0.0.1:8765). With locks being
serialized to "locks.db". These options can be modified using command line arguments.

.. code-block:: bash
	$ locker/__init__.py --ip 0.0.0.0 --port 8080 --file mylocks.dat
	
Locker can also be used as a component of a larger system. Import the Locker object and initialize
with runserver=False. If your system uses CherryPy the api methods of Locker are already decorated
with @expose. Note that even running without its web server Locker API methods return jsonified
data. See help(Locker) for more details.

.. code-block:: python
	from locker import Locker
	
	locker = Locker(runserver=False)
	

Basic Usage
-----------

Locker exposes three API methods to lock, unlock and query for resources. Respectively these are 
"canhaz", "nowant" and "dohaz". The requests module is recommended when using Python to call the
Locker API but anything capable of HTTP calls will work.

Locking Resources
#################

Locking or reserving resources is done with the canhaz call. This call checks if the resource is
locked and if unlocked returns OK and a token to use when unlocking the resource. WARNING: the
resource cannot be unlocked without this token.

The example below locks the resource "/my/resource".

.. code-block:: python
	>>> response = get("http://localhost:8765/canhaz/my/resource")
	>>> response.json()
	{u'token': u'cb7edb5c-6b7c-4b60-b127-3a7e344f00d0', u'ok': True}
	
If another attempt is made to lock the same resource (or a parent or child of /my/resource) the
request will fail.

.. code-block:: python
	>>> response = get("http://localhost:8765/canhaz/my/resource")
	>>> response.json()
	{u'ok': False, u'lockedBy': u'?'}
	
More on the lockedBy field in the Advanced Usage section.


Unlocking Resources
###################

Unlocking resources is done with the nowant call. This call succeeds if the resource is locked and
the token is valid to unlock it.

.. code-block:: python
	>>> response = get("http://localhost:8765/nowant/my/resource?token=cb7edb5c-6b7c-4b60-b127-3a7e344f00d0")
	>>> response.json()
	{u'ok': True}
	
If the resource is not locked or the token is invalid the call will fail.

.. code-block:: python
	>>> response = get("http://localhost:8765/nowant/my/resource?token=invalid-token")
	>>> response.json()
	{u'ok': False}

	
Querying the State of Resources
###############################

The state of any resource can be retrieved by a dohaz call. This call provides the id of the caller
that locked the resource (if available), "?" if the id of the caller is not known or None if the
resource is not locked.

The example below show a locked resource.

.. code-block:: python
	>>> response = get("http://localhost:8765/dohaz/my/resource")
	>>> response.json()
	{u'lockedBy': u'?'}
	
This example shows an unlocked resource.

.. code-block:: python
	>>> response = get("http://localhost:8765/dohaz/some/resource")
	>>> response.json()
	{u'lockedBy': None}
	
	
Advanced Usage
--------------

In addition to the standard functionality documented above Locker supports identification of the
caller that owns a resource lock as well as modifications of the locking behavior.

Caller Identification
#####################

In several of the basic examples the lockedBy field was returned showing only "?". To properly
identify the owner of a resource lock the caller can provide an id when locking the resource. The
id will then be returned in future queries to canhaz and dohaz as the lockedBy field.

.. code-block:: python
	>>> response = get("http://localhost:8765/canhaz/this?id=timmy")
	>>> response.json()
	{u'token': u'15b536b9-97b3-430b-8c5f-14261c97f782', u'ok': True}
	
	>>> response = get("http://localhost:8765/dohaz/this")
	>>> response.json()
	{u'lockedBy': u'timmy'}
	
IDs are arbitrary strings and are optional when locking a resource.


Locking Behavior Modifications
##############################

Athough not common you may have a need to lock a resource without locking its parents or without
locking its children. This is supported when locking the resource by passing additional arguments to
the canhaz call.

This is an example of locking a resource without locking its parent(s):

.. code-block:: python
	>>> get("http://localhost:8765/canhaz/foo/bar?lockParents=False")
	
	>>> response = get("http://localhost:8765/canhaz/foo")
	>>> response.json()
	{u'token': u'd305eb3a-2fec-4db1-9448-47cec24c169f', u'ok': True}
	
And this is an example of locking a resource without locking its child(ren):

.. code-block:: python
	>>> get("http://localhost:8765/canhaz/bar?lockChildren=False")
	
	>>> response = get("http://localhost:8765/canhaz/bar/foo")
	>>> response.json()
	{u'token': u'72ad7aaa-3529-4f84-ae6b-23200fcbb731', u'ok': True}
	
These flags can be used together if desired.

