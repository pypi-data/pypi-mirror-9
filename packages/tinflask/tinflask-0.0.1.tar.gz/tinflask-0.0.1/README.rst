tinflask 0.0.1
==============

Tornado server with some built-in endpoints.

Here's a simple usage example::

	import tinflask.web

	def test():
		self.write("hola")

	def test_job():
		print("did some job")

	if __name__ == "__main__":
		a = tinflask.web.Application()
		c.add_status_job("Test Job", 5, test_job)
		c.run()

The Application looks at the environment variables `HOST`, `PORT`, and `ENDPOINT` on initialization.
If These are not set the defaults are `HOST`: 0.0.0.0, `PORT`: 8080, `ENDPOINT`: /.

get tinflask
============

Install `flask`_ and `requests`_

    sudo easy_install tinflask

Download the latest release from `Python Package Index`_
or clone `the repository`_

More documentation is on it's way *(check the* `site`_ *for updates)*

Provide any feedback and issues on the `bug tracker`_, that should be coming soon.


.. _flask: http://flask.pocoo.org/
.. _requests: http://docs.python-requests.org/en/latest/
.. _site: https://github.com/juztin/tinflask
.. _the repository: https://github.com/juztin/tinflask
.. _bug tracker: https://github.com/juztin/tinflask/issues
.. _Python Package Index: http://pypi.python.org/pypi/tinflask
