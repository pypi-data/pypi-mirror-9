===========
EPIC Sample
===========

This package is a companion to the django-epic package.  It's purpose
is to provide a minimal but completely functional environment that
let's a potential user of EPIC get a feel for how the application
works.

Install this package with:

	pip install --user django-epic-sample

If you do not have the "pip" command installed on your system,
download and install the latest version of Python from:

	https://www.python.org/downloads/

After installation, start the Django test server with:

	cd INSTALL_TARGET
	python manage.py runserver

where INSTALL_TARGET is the path to the directory the package was
installed in.  Assuming Python v3.4, you can find the package
directory at:

On Linux and Mac OS X:
	~/.local/lib/python3.4/site-packages/epic-sample/

On Windows:
	AppData\Roaming\Python\Python34\site-packages\epic-sample\

Then point your web-browser at:

	http://localhost:8000/epic/

This page should prompt you to log in.  You can use:

	- username = admin
	- password = admin

for this sample site.
