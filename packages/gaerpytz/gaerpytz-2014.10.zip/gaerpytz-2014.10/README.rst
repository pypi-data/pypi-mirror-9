gaerpytz
========

gaerpytz is like gaepytz (a version of pytz that works well on Google App
Engine) but automated so zoneinfo is up-to-date.

The problem
-----------

During initialization, pytz opens more than 500 zoneinfo files to check if they
exist. Opening so many files is a problem when using pytz on Google App Engine.

The workaround is to package all zoneinfo files in a zip archive. gae-pytz is
the most well-known example of this approach but it has not been updated in a
long time.

The solution
------------

gaerpytz uses the same idea and makes 2 changes to pytz:

- Package all zoneinfo files in zoneinfo.zip
- Modify __init__.py to read from zoneinfo.zip

Just download the modified code and put it in your ``pytz`` directory. **You
don't need to change the code that uses pytz.** (The package name gaerpytz is
superficial and the package structure has not been changed.)

- Import the package with ``import pytz``
- Use it like you would pytz

In practice, gaerpytz runs slightly slower due to the zip file.

So what? You can do this yourself, right?
-----------------------------------------

Time zones are magic (change frequently based on local laws), so pytz is
updated often. Applying these modifications to every new pytz release is
tedious. This is why you see many out-of-date or abandoned packages that patch
pytz on PyPI.

gaerpytz takes people out of the process. **gaerpytz watches pytz. When a new
version of pytz is released, gaerpytz automatically fetches a copy and builds
itself.** This is what makes gaerpytz Google App Engine *-r* than the pytz
patches that came before.

You can view the code directly at
`http://gaerpytz.appspot.com/ <http://gaerpytz.appspot.com/>`_.

*Even if you don't use the code, please help me by contributing location data
to the time zone database.*
