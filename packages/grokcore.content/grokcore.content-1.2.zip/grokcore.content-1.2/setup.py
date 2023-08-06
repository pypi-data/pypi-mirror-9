import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = "%s\n%s\n" % (read('README.txt'), read('CHANGES.txt'))

install_requires = [
    'setuptools',
    'ZODB3',
    'grokcore.component >= 2.1',
    'zope.annotation',
    'zope.container',
    'zope.interface',
    'zope.lifecycleevent',
    ]

tests_require = [
    'zope.testing',
    'zope.component',
    ]

setup(
    name='grokcore.content',
    version='1.2',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grokcore.content',
    description='Base content types for Grok',
    long_description=long_description,
    license='ZPL',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3'],
)
