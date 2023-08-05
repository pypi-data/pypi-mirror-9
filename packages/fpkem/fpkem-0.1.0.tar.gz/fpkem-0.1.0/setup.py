from distutils.core import setup
from distutils.extension import Extension

try:
	from Cython.Build import cythonize
except ImportError:
	has_cython = False
else:
	has_cython = True

ext = '.pyx' if has_cython else '.c'

ext_modules = [
	Extension("fpkem.bitset", [ "fpkem/bitset" + ext, "fpkem/lib/binBits.c", "fpkem/lib/bits.c", "fpkem/lib/common.c" ], include_dirs=[ "fpkem/lib" ] ),
	Extension("fpkem.intersection", [ "fpkem/intersection" + ext ] ),
]

if has_cython:
	ext_modules = cythonize(ext_modules)

with open("README.txt") as f:
	long_description = f.read()

setup(	name = 'fpkem',
	version = '0.1.0',
	description = 'Estimation of gene expression based on RNA-Seq data',
	author = 'Maciej Paszkowski-Rogacz',
	author_email = 'maciej.paszkowski-rogacz@tu-dresden.de',	
	url = 'http://www.buchholz-lab.org/',
	package_dir = { 'fpkem': 'fpkem' },
	packages = ['fpkem', 'fpkem', 'fpkem'],
	scripts = ['bin/fpkem'],
	ext_modules = ext_modules,
	requires = [ 'pysam (>=0.7.6)' ],
	classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: Implementation :: CPython",
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Natural Language :: English",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: Artistic License",
		"Operating System :: POSIX :: Linux",
		"Topic :: Scientific/Engineering",
		"Topic :: Scientific/Engineering :: Bio-Informatics",
	],
	license = "The Artistic License 2.0",
	platforms = ['Linux'],
	long_description = long_description,
)
