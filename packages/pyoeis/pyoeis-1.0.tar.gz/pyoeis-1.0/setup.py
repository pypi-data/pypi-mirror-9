from distutils.core import setup


setup(
    name='pyoeis',
    packages=['PyOEIS', ],
    version='1.0',
    author='Dylan Evans',
    author_email='dylan@physicynicism.com',
    url='www.physicynicism.com',
    description='Python interface to the OEIS',
    long_description='''
    PyOEIS provides several methods to search the `Online
    Encyclopedia of Integer Sequences with Python (OEIS)
    <http://www.oeis.org>`_. It also allows for access
    the information contained within individual sequence
    entries, obtained by the querying methods
    provided.''',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Natural Language :: English',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering :: Mathematics',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2']
    )
