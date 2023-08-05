try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'django_jsend',
	packages = ['django_jsend'],
	version = '0.2',
	description = 'Django view for JSend specification',
	author = 'Maikel Martens',
	author_email = 'maikel@martens.me',
	url = 'https://github.com/krukas/django-jsend',
	download_url = 'https://github.com/krukas/django-jsend/tarball/0.2',
	keywords = ['Django', 'view', 'JSend'],
	classifiers = [],
	install_requires=[
          'Django',
      ],
)