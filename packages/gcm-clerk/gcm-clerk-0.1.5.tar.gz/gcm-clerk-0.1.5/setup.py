try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='gcm-clerk',
    version='0.1.5',
    author='Aleksi Hoffman',
    author_email='aleksi@lekksi.com',
    url='https://bitbucket.org/aleksihoffman/gcm-clerk',
    description='Python client for Google Cloud Messaging (GCM)',
    long_description=open('README.rst').read(),
    packages=['gcm_clerk'],
    license="Apache 2.0",
    keywords='gcm push notification google cloud messaging android',
    install_requires=['requests'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
