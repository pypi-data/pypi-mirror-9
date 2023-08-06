"""Hierarchical resource locking mechanism.

Author: Justin Giorgi
License: GNU GPLv3
"""

# Standard library imports
from json import dumps
from optparse import OptionParser
from uuid import uuid4
try:
	from cPickle import load, dump
except ImportError:
	from pickle import load, dump

# Installed extensions
import cherrypy


# Defaults
IP = "127.0.0.1"
PORT = 8765
FILE = "locks.db"


class Locker(object):
	"""Defines an object listening for HTTP requests to lock, unlock and get the status of arbitrary
	resources. Resources exist in a hierarchy. When a resource is locked children of that resource
	are considered locked (unless lockChildren=False is passed when locking the resource). Parents
	of a locked resource are considered partially locked (unless lockParents=False is passed when
	locking the resource). They may not be locked however their children may be locked.
	
	Locks are serialized to disk using (c)Pickle. Note this file is overwritten on each lock/unlock.
	Changing it while this object is running will not effect the state of resource locks.
	
	Initialization params:
		ip (str): IP address to bind to.
		port (int): Port to bind to.
		file (str): Filename to serialize data out to.
		runserver (bool): Default True, run or do not run the cherrypy web server
		serialize (bool): Default True, do or do not serialize the locks cache
	"""

	def __init__(self, ip=IP, port=PORT, file=FILE, runserver=True, serialize=True):
		self.ip = ip
		self.port = port
		self.file = file
		self.serialize = serialize
		
		self._read_db() # Get locks and partial locks
		# Lock format: (path, to, lock): {id: str, lockParents: bool, lockChildren: bool}
		# Partial Lock format: (path, to, parent): (full, path, to, lock)
		
		# Start cherrypy 
		if runserver:
			cherrypy.server.socket_host = self.ip
			cherrypy.server.socket_port = self.port
			cherrypy.quickstart(self, "/")
		

	def _write_db(self):
		"""Write the locks to the database file.
		"""
		if self.serialize:
			dump((self.locks, self.partial_locks), open(self.file, "wb"))
		
	
	def _read_db(self):
		"""Read data from the locks database file.
		"""
		if self.serialize:
			try:
				self.locks, self.partial_locks = load(open(self.file, "rb"))
			except IOError:
				self.locks, self.partial_locks = {}, {}
		else:
			self.locks, self.partial_locks = {}, {}
		
		
	def _check_locked(self, *path):
		"""Determine whether a particular path is locked. Return False or ID of locker.
		"""
		lockedBy = None
		
		# Check if the full path is partially locked
		if path in self.partial_locks:
			lockedBy = self.locks[self.partial_locks[path][0]]["id"]
			
		# Check if part of the path is locked and children of that part are locked or if the whole
		# path is explicitly locked locked
		else:
			checkpath = []
			for p in path:
				checkpath.append(p)
				cp = tuple(checkpath)
				if cp in self.locks and (cp == path or self.locks[cp]["lockChildren"]):
					lockedBy = self.locks[cp]["id"]
					break
		
		return lockedBy
		
		
	def _lock(self, id, lockParents, lockChildren, token, *path):
		"""Lock the given path to the given id.
		"""
		lockData = {
			"id": id,
			"token": token,
			"lockParents": lockParents,
			"lockChildren": lockChildren
			}
		
		# Lock the exact path provided
		self.locks[path] = lockData
		
		# If lockParents lock the root of the path
		if lockParents:
			lockpath = []
			for p in path:
				lockpath.append(p)
				lp = tuple(lockpath)
				if lp not in self.partial_locks:
					self.partial_locks[lp] = [path]
				else:
					self.partial_locks[lp].append(path)
			
		# Sync DB
		self._write_db()
		
		
	def _unlock(self, *path):
		"""Unlock the given path.
		"""
		# Check if the parents were locked, if so unlock the root of the path
		if self.locks[path]["lockParents"]:
			lockpath = []
			for p in path:
				lockpath.append(p)
				lp = tuple(lockpath)
				self.partial_locks[lp].remove(path)
				if not self.partial_locks[lp]:
					del self.partial_locks[lp]
		
		# Unlock the exact path
		del self.locks[path]
			
		# Sync DB
		self._write_db()
		
		
	@cherrypy.expose
	def canhaz(self, *path, **kwargs):
		"""Attempt to lock a given path, return OK with an unlock token if available or not OK if
		already locked.
		
		All non keyword arguments will be interpreted as a hierarchical path to the desired resource
		
		kwargs:
			lockParents (bool), Default: True, lock all parent resources from being exclusively
				locked. Parent resources can still have their children locked.
				
			lockChildren (bool), Default: True, lock all child resources from being locked. 
			
			id (str), Default: "?", Identity of the object locking this resource.
			
		Return value:
			{
				"ok": bool (the resource was locked successfully),
				
				if already locked:
					"lockedBy": str (the id of the object that has locked the resource)
					
				else:
					"token": str ("key" to unlock the resource)
			}
		"""
		ret = {"ok": True}
		
		# Set and confirm kwarg
		lockParents = kwargs.pop("lockParents", True)
		if lockParents == "False": lockParents=False
		lockChildren = kwargs.pop("lockChildren", True)
		if lockChildren == "False": lockChildren=False
		id = kwargs.pop("id", "?")
			
		# Check if the lock is already taken, return if so
		lockedBy = self._check_locked(*path)
		if lockedBy:
			ret["ok"] = False
			ret["lockedBy"] = id
			return dumps(ret)
			
		# Otherwise lock it
		ret["token"] = str(uuid4())
		self._lock(id, lockParents, lockChildren, ret["token"], *path)
		return dumps(ret)
		
		
	@cherrypy.expose
	def nowant(self, *path, **kwargs):
		"""Unlock a given path with the token provided in kwargs.
		
		All non keyword arguments will be interpreted as a hierarchical path to the desired resource
		
		kwargs:
			token (str), Default: None, token granted when locking the resource REQUIRED to unlock!
			
		Return value:
			{
				"ok": bool (the resource was unlocked successfully, will be false if the resource is
					not locked or if the token is invalid)
			}
		"""
		ret = {"ok": True}
		
		# Set and confirm kwargs, return error
		token = kwargs.pop("token", None)
			
		# Verify the token, if path not locked or token not valid return not OK
		if path not in self.locks or self.locks[path]["token"] != token:
			ret["ok"] = False
			return dumps(ret)
			
		# Unlock it
		self._unlock(*path)
		return dumps(ret)
			
	
	@cherrypy.expose
	def dohaz(self, *path):
		"""Return the current owner of a lock (their ID) or None if not locked.
		
		All non keyword arguments will be interpreted as a hierarchical path to the desired resource
			
		Return value:
			{
				"lockedBy": str or None (the id of the object that has the resource locked or None)
			}
		"""
		ret = {"lockedBy": self._check_locked(*path)}
		return dumps(ret)
		
		
if __name__ == "__main__":
	# Get command line arguments
	parser = OptionParser()
	parser.add_option(
		"-i",
		"--ip",
		dest="ip",
		default=IP,
		action="store",
		type="string",
		help="IP Address to bind to. Default: 127.0.0.1"
	)
	parser.add_option(
		"-p",
		"--port",
		dest="port",
		default=PORT,
		action="store",
		type="int",
		help="Port to bind to. Default: 8765"
	)
	parser.add_option(
		"-f",
		"--file",
		dest="file",
		default=FILE,
		action="store",
		type="string",
		help="Data file to store locks in. Default: locks.db"
	)
	(options, args) = parser.parse_args()
	IP = options.ip
	PORT = options.port
	FILE = options.file
	Locker()