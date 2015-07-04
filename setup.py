import os, sys
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

version = __import__('klingon').__version__
readme = read_file('README.rst')
history = read_file('HISTORY.rst').replace('.. :changelog:', '')

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

setup(
    name='django-klingon',
    version=version,
    author='Rafael Capdevielle, Angel Velasquez',
    author_email='angvp@archlinux.org',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/angvp/django-klingon',
    license='GPL',
    description="""django-klingon is an attempt to make django model translation
    suck but with no integrations pain in your app!""",
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=readme + '\n\n' + history,
    test_suite="runtests.runtests",
    zip_safe=False,
)
