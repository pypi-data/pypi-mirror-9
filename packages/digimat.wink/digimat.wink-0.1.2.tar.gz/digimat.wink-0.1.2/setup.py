from setuptools import setup, find_packages

setup(
    name='digimat.wink',
    version='0.1.2',
    description='Digimat Wink',
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
