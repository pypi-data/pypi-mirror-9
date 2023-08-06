from distutils.core import setup

setup(
    name='TemperatureConverter',
    version='0.1.1',
    author='Steven Cipriano',
    author_email='cipriano.steven@gmail.com',
    packages=['temperatureconverter'],
    scripts=['bin/demo.py'],
    url='http://pypi.python.org/pypi/TemperatureConverter',
    license='LICENSE.txt',
    description='Temperature unit converter.',
    long_description=open('README.txt').read(),
    install_requires=[]
)
