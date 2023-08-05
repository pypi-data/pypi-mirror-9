capuchin 0.0.6
==============

Tornado server with some built-in endpoints.

Here's a simple usage example::

	import capuchin.web

	class TestHandler(tornado.web.RequestHandler):
		def get(self):
			self.write("hola")

	def test_job():
		print("did some job")

	if __name__ == "__main__":
		c = capuchin.web.Application([
			(r"/test", TestHandler),
		])
		c.add_status_job("Test Job", 5, test_job)
		c.listen()

The Application looks at the environment variables `HOST`, `PORT`, and `ENDPOINT` on initialization.
If These are not set the defaults are `HOST`: 0.0.0.0, `PORT`: 8080, `ENDPOINT`: /.

get capuchin
============

Install `tornado`_ and `requests`_

    sudo easy_install capuchin

Download the latest release from `Python Package Index`_
or clone `the repository`_

More documentation is on it's way *(check the* `site`_ *for updates)*

Provide any feedback and issues on the `bug tracker`_, that should be coming soon.


.. _tornado: http://www.tornadoweb.org/en/stable/
.. _requests: http://docs.python-requests.org/en/latest/
.. _site: https://bitbucket.org/juztin/py-capuchin
.. _the repository: https://github.com/juztin/py-capuchin
.. _bug tracker: https://github.com/juztin/py-capuchin/issues
.. _Python Package Index: http://pypi.python.org/pypi/capuchin
