from distutils.core import setup

setup(
    name='pysmsru',
    version='0.1.5',
    author='Andrey Lukyanov',
    author_email='laandrey@gmail.com',
    packages=['pysmsru', 'pysmsru.tests'],
    url='http://pypi.python.org/pypi/pysmsru/',
    description='send sms with sms.ru service.',
    long_description=open('README.txt').read(),
)