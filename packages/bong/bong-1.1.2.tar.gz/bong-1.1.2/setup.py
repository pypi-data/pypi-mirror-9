from bong.metadata import VERSION, SUMMARY

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(name='bong',
      version=VERSION,
      description=SUMMARY,
      long_description=long_description,
      author='Alistair Lynn',
      author_email='arplynn@gmail.com',
      license='MIT',
      url='https://github.com/prophile/bong',
      zip_safe=True,
      entry_points={'console_scripts':
          'bong=bong.cli:main'
      },
      setup_requires=[
          'nose >=1,<2'
      ],
      packages=find_packages(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: X11 Applications :: Gnome',
          'Environment :: MacOS X',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Topic :: Office/Business'
      ])
