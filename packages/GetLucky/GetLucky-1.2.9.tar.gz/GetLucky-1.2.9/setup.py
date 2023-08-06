from setuptools import setup

setup(
    name='GetLucky',
    version='1.2.9',
    author='Tanner Baldus',
    author_email='tbaldu285@gmail.com',
    packages=['getLucky'],
    scripts=[],
    url='http://pypi.python.org/pypi/getlucky/',
    license='LICENSE.txt',
    description='A CLI to quickly set the mood with Songza.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.2.1",
        "beautifulsoup4 >= 4.3.2",
        "docopt >= 0.6.1",
    ],
    entry_points={
        'console_scripts': [
         'gl = getLucky.getLucky:main',
        ],
        }
)