from distutils.core import setup

setup(
    name='dsmsmessages',
    version='0.1.54',
    author='Chris Horsley',
    author_email='chris.horsley@csirtfoundry.com',
    packages=['dsmsmessages', 'dsmsmessages.test'],
    scripts=[],
    url='http://bitbucket.org/dsms/dsmsmessages/',
    license='LICENSE.txt',
    description='Messaging services for DSMS',
    long_description=open('README.txt').read(),
    install_requires=[
        "jsonschema==2.3.0",
        "iso8601==0.1.10",
    ]
)
