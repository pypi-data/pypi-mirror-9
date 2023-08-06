from distutils.core import setup

setup(
    name='bitterGravel',
    version='1.0.0',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['bittergravel'],
    scripts=['bin/bittergravel'],
    url='http://pypi.python.org/pypi/bitterGravel/',
    license='GPLv3',
    description='bitterGravel',
    long_description=open('README.md').read(),
    install_requires=[],
)

