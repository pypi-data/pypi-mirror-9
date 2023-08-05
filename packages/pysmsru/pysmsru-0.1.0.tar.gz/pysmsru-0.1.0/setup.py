from distutils.core import setup

setup(
    name='pysmsru',
    version='0.1.0',
    author='Andrey Lukyanov',
    author_email='laandrey@gmail.com',
    packages=['smsru', 'smsru.tests'],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/pysmsru/',
    # license='LICENSE.txt',
    description='send sms with sms.ru service.',
    long_description=open('readme.txt').read(),
    # install_requires=[
    #     "urllib2",
    #     "urllib",
    # ],
)