from setuptools import setup, find_packages

setup(
    name='digimat.ccu',
    version='0.1.12',
    description='Digimat Homematic CCU2',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@splust.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir = {'':'src'},
    install_requires=[
        'requests',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
