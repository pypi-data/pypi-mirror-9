from os.path import join as path_join, dirname
from setuptools import setup, find_packages


def read(filename):
    return open(path_join(dirname(__file__), filename)).read()


setup(
    name='gears-react',
    version='0.2.2',
    url='https://github.com/mandx/gears-react',
    license='ISC',
    author='Armando Perez Marques',
    author_email='gmandx@gmail.com',
    description='Gears compiler for React/JSX',
    long_description=read('README.md'),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip()
        for line in read('requirements.txt').splitlines()
        if bool(line.strip())
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
    ],
)
