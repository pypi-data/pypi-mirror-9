from distutils.core import setup

setup(
    name='PicasaDeleter',
    version='0.1.0',
    author='Matthew Russell',
    author_email='matt@fredsherbet.com',
    packages=[],
    scripts=['bin/picasa-deleter.py'],
    url='http://pypi.python.org/pypi/PicasaDeleter/',
    license='LICENSE.txt',
    description='Delete ALL the photos in your Picasa/Google+ account',
    long_description=open('README.txt').read(),
    install_requires=[
        "gdata >= 2.0.8",
    ],
)

