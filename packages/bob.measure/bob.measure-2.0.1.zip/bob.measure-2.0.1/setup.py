#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

bob_packages = ['bob.core', 'bob.math']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['blitz >= 0.10', 'boost']

setup(

    name='bob.measure',
    version=version,
    description='Bob\'s evalution metrics',
    url='http://github.com/bioidiap/bob.measure',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,

    namespace_packages=[
      "bob",
    ],

    ext_modules = [
      Extension("bob.measure.version",
        [
          "bob/measure/version.cpp",
        ],
        packages = packages,
        version = version,
        bob_packages = bob_packages,
      ),

      Extension("bob.measure._library",
        [
          "bob/measure/error.cpp",
          "bob/measure/main.cpp",
        ],
        packages = packages,
        version = version,
        bob_packages = bob_packages,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    entry_points={
      'console_scripts': [
        'bob_compute_perf.py = bob.measure.script.compute_perf:main',
        'bob_eval_threshold.py = bob.measure.script.eval_threshold:main',
        'bob_apply_threshold.py = bob.measure.script.apply_threshold:main',
        'bob_plot_cmc.py = bob.measure.script.plot_cmc:main',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],

  )
