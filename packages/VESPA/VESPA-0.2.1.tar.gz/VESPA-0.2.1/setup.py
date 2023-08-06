from setuptools import setup, Extension, find_packages

on_rtd = False
try:
    from Cython.Distutils import build_ext
    import numpy
except ImportError:
    on_rtd = True
    numpy = None
    build_ext = None
    
import os

def readme():
    with open('README.rst') as f:
        return f.read()

# Hackishly inject a constant into builtins to enable importing of the
# package before the library is built.
import sys
if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
builtins.__VESPA_SETUP__ = True
import vespa
version = vespa.__version__


# Publish the library to PyPI.
if "publish" in sys.argv[-1]:
    os.system("python setup.py sdist upload")
    sys.exit()

# Push a new tag to GitHub.
if "tag" in sys.argv:
    os.system("git tag -a {0} -m 'version {0}'".format(version))
    os.system("git push --tags")
    sys.exit()

if not on_rtd:
    transit_utils = [Extension('vespa_transitutils',['vespa/vespa_transitutils.pyx'],
                                include_dirs=[numpy.get_include()])]
else:
    transit_utils = None
        
setup(name = "VESPA",
      version = version,
      description = "Calculate astrophysical false positive probabilities for transiting exoplanet signals",
      long_description = readme(),
      author = "Timothy D. Morton",
      author_email = "tim.morton@gmail.com",
      url = "https://github.com/timothydmorton/VESPA",
      #packages = ['vespa', 'vespa/stars',
      #            'vespa/orbits'],
      packages = find_packages(),
      package_data = {'vespa': ['data/*', 'tests/*.ini',
                                'tests/*.h5', 'tests/*.pkl'],
                      'vespa.stars': ['data/*'],
                      'vespa.orbits':['data/*']},
      ext_modules = transit_utils,
      scripts = ['scripts/get_trilegal',
                 'scripts/koifpp',
                 'scripts/batch_koifpp_condor',
                 'scripts/calcfpp'],
      cmdclass = {'build_ext': build_ext},
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy'
        ],
      install_requires=['cython','pandas>=0.13','simpledist>=0.1.11', 'emcee', 'isochrones>=0.7.6', 'acor'],
      zip_safe=False
) 
