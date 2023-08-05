from distutils.core import setup

with open('dirtyebay/version.py') as f:
    # get __version__ var into our scope without importing
    exec(f.read())

setup(
    name='dirtyebay',
    version=__version__,  # noqa
    packages=['dirtyebay'],
    license='MIT',
    long_description=open('pypi.rst').read(),
    description='An eBay API client which respects (XSD) schema and talks SOAP but doesn\'t use Suds',
    author='Anentropic',
    author_email='ego@anentropic.com',
    url='https://github.com/anentropic/dirtyebay',
    install_requires=[
        'lxml',
        'dogpile.cache',
        'appdirs',
        'requests',
    ],
)
