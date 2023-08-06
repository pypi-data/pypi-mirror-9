from setuptools import setup, find_packages

setup(
    name='digimat.blink1',
    version='0.1.4',
    description='Digimat Blink1',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@splust.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir = {'':'src'},
    install_requires=[
        'pyusb>=1.0.0b1',
        'webcolors',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
