from distutils.core import setup, Extension
import os, numpy

Name = 'fast_prng'

# Delete fast_prng.c to re-cythonize code, this script will automatically regenerated fast_prng.c using your cython package.
USE_CYTHON = False if Name+'.c' in os.listdir(os.getcwd()) else True

ext = '.pyx' if USE_CYTHON else '.c'
extensions = [Extension(Name, [Name+ext], extra_compile_args=['-O2'] )]

if USE_CYTHON:
	from Cython.Build import cythonize
	extensions = cythonize(extensions)

setup(
	name=Name,
	version='1.0.17',
	description='Fast exponentially- and normally-distributed Pseudo Random Number Generator',
	author='Christopher McFarland',
	author_email='christopherdmcfarland+pypi@gmail.com',	
	maintainer_email='christopherdmcfarland+pypi@gmail.com',	
	classifiers =[
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Cython',
		'Programming Language :: C',
		'License :: OSI Approved',
		'License :: OSI Approved :: MIT License',
		'Operating System :: Unix',
		'Intended Audience :: Science/Research',
		'Natural Language :: English',
		'Topic :: Scientific/Engineering',
		],
	license = 'MIT License',	
	requires=['numpy'],
	include_dirs=[numpy.get_include()],
	url = 'https://bitbucket.org/cdmcfarland/fast_prng',
	ext_modules = extensions 
)

