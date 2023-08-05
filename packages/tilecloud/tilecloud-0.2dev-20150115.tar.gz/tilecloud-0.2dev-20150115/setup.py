from setuptools import setup, find_packages
from glob import glob
import os

version = '0.2'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

install_requires = open(os.path.join(here, 'requirements.txt')).read().splitlines()

setup(
        name='tilecloud',
        version=version,
        description='Tools for managing tiles',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: GIS',
        ],
        author='Tom Payne',
        author_email='twpayne@gmail.com',
        url='http://github.com/twpayne/tilecloud',
        license='BSD',
        packages=find_packages(exclude=['tiles', 'tilecloud.tests']),
        zip_safe=True,
        install_requires=install_requires,
        test_suite='tilecloud.tests',
        scripts=glob('tc-*'),
        entry_points="""
        # -*- Entry points: -*-
        """,
        long_description=README,
        )
