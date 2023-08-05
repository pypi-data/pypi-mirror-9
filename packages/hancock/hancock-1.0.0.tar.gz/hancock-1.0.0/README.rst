hancock 1.0.0
=============

HTTP request signing library.

Here's a simple usage example::

	import hancock

	if __name__ == "__main__":
		url = "http://localhost:8000/service/"
		qs = { "color": "green" }

		url = hancock.sign(public_key, private_key, url, query)
		print(url)

		r = hancock.get(public_key, private_key, url, query)
		print(r.json())


get hancock
===========

Install `requests`_::
Install `simplejson`_::

    sudo easy_install hancock

Download the latest release from `Python Package Index`_ 
or clone `the repository`_

More documentation is on it's way *(check the* `site`_ *for updates)*

Provide any feedback and issues on the `bug tracker`_, that should be coming soon.


.. _requests: http://docs.python-requests.org/en/latest/
.. _simplejson: http://simplejson.readthedocs.org/en/latest/
.. _site: https://bitbucket.org/juztin/py-hancock
.. _the repository: https://bitbucket.org/juztin/py-hancock
.. _bug tracker: https://bitbucket.org/juztin/py-hancock
.. _Python Package Index: http://pypi.python.org/pypi/hancock
