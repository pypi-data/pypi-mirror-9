# from distutils.core import setup
from setuptools import setup
from cma import __version__
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

with open('README.txt') as file:
    long_description = file.read()  # now assign long_description=long_description below

setup(name="cma",
      long_description=long_description,  # __doc__, # can be used in the cma.py file
      version=__version__.split()[0],
      description="CMA-ES, Covariance Matrix Adaptation Evolution Strategy for non-linear numerical optimization in Python",
      author="Nikolaus Hansen",
      author_email="hansen at lri.fr",
      maintainer="Nikolaus Hansen",
      maintainer_email="hansen at lri.fr",
      url="https://www.lri.fr/~hansen/cmaes_inmatlab.html#python",
      # license="MIT",
      license="BSD",
      classifiers = [
          "Intended Audience :: Science/Research",
          "Intended Audience :: Education",
          "Intended Audience :: Other Audience",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: BSD License",
          # "License :: OSI Approved :: MIT License",
      ],
      keywords=["optimization", "CMA-ES", "cmaes"],
      py_modules=["cma"],
      requires=["numpy"],
#      package_data={
#        'images': ['cma-on-rosen-8D.png'],
#      },
)

# packages = ['cma'],  # indicates a multi-file module and that we have a cma folder and cma/__init__.py file
