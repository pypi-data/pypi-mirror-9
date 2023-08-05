from distutils.core import setup

setup(
    name='CatStalker',
    version='0.0.2',
    author='J. Pike',
    author_email='pip@chilon.net',
    scripts=['bin/catstalker.py'],
    url='http://github.com/nuisanceofcats/catstalker',
    license='LICENSE.txt',
    description='Control energenie radio control board.',
    long_description=open('README.txt').read(),
    install_requires=["raspberry-gpio >= 0.5.0"],
)
