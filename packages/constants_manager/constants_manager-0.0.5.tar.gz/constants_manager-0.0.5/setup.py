from setuptools import setup, find_packages
import sys

setup(name='constants_manager',
      version='0.0.5',
      description='a library of managing constants.',
      long_description="""This library is help you to use managing constants. Especially when you creating web application.""",
      author='Kenichi Masuda',
      author_email='masuken@gmail.com',
      url='https://github.com/masudaK/constants_manager',
      packages=find_packages(),
      zip_safe=(sys.version>="2.5"),
      license='GNU Lesser General Public License v3 or later (LGPLv3+)',
      keywords='',
      platforms='Linux',
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Programming Language :: Python :: 3'
                   ]
      )

