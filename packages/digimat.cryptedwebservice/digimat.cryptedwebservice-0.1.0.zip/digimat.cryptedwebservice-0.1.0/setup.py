from setuptools import setup, find_packages

setup(
    name='digimat.cryptedwebservice',
    version='0.1.0',
    description='Digimat Homematic Crypted Webservice',
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
