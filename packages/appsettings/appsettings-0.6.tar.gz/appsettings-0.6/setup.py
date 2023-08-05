from setuptools import setup, find_packages

setup(
    name='appsettings',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    version='0.6',
    license='MIT',
    url='http://bits.btubbs.com/appsettings/',
    packages=find_packages(),
    description=('Argparse wrapper that supports fallback settings in env vars '
                 'and/or a yaml file.'),
    long_description=open('README.rst').read(),
    install_requires=[
        'pyyaml>=3.0',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],
    zip_safe=False,
)
