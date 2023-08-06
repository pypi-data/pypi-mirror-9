0.12.0 (2015-04-01)
-------------------
- New Features:

  - Method `get_mongodb_client` to get a MongoDB connection client.

- Bugfixes:

  - None

- Incompatible changes:

  - `Okapi.__init__` has changed to have a new mandatory `db` parameter.
   Parameters `mongodb_uri` and `connect_timeout_ms` have been removed.

0.11.0 (2014-12-29)
-------------------
- New Features:

  - Changed blank space to a T letter as indicator of the beginning of the time 
    element to be more iso-friendly:
    http://www.ecma-international.org/ecma-262/5.1/#sec-15.9.1.15

0.10.0 (2014-11-11)
-------------------
- New Features:

  - Don't hardcode the name of the database but expect it to be in
    the mongodb_uri parameter.

0.9.0 (2014-10-16)
------------------
- New Features:

  - Decouple okapi from requests so that any library following requests 
    interface can be used. This introduces a backward incompatible change
    because now the __init__ method for okapi Api class requires a new
    argument

0.8.0 (2014-09-26)
------------------
- New features:

  - Use one collection per project instead of saving all projects in the same collection
  - Add a time_bucket attribute to make time based queries faster

0.7.1 (2014-07-28)
----------------
- Bug Fixes:

	-Make sure to raise the exception if an error occurs so the user know 
	exactly what is happening instead of code crashing
