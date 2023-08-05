from setuptools import setup

setup(
	description = 'A helper function for common uses of subprocess',
	author = 'Mike Lang',
	author_email = 'mikelang3000@gmail.com',
	py_modules = ['easycmd'],
	version = '0.0.1421587592',
	long_description = 'A helper function for common uses of subprocess\n\nThis aims to make some commonly desired functionality easier to do without needing\nto manually create Popen objects, while being more flexible than check_call() and check_output().\n\nShould work fine with gevent.subprocess with monkey patching.\n',
	name = 'easycmd',
)
