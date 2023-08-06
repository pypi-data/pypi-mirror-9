===========
EPIC Sample
===========

This package is a companion to the django-epic package.  It's purpose
is to provide a minimal but completely functional environment that
let's a potential user of EPIC get a feel for how the application
works.

Install this package with:

	pip3 install django-epic-sample

(or use "pip" if you're stuck on Python2).

To install without requiring root privileges, you can use:

	pip3 install --user django-epic-sample

After installation, start the Django test server with:

	cd INSTALL_TARGET
	python3 manage.py runserver

where INSTALL_TARGET is the path to the directory the package was installed
in, for example:

	~/.local/lib/python3.4/site-packages/epic-sample/

Then point your web-browser at:

	http://localhost:8000/epic/

This page should prompt you to log in.  You can use:

	- username = admin
	- password = admin

for this sample site.

		--- end of file ---