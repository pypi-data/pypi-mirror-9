from distutils.core import setup, Extension
import numpy
setup(name='chopthin',
      version='0.2',
      description='Implementation of the chopthin resampler for particle filtering/SMC',
      author='Axel Gandy',
      author_email='a.gandy@imperial.ac.uk',
      url='http://wwwf.imperial.ac.uk/~agandy/software.html',
      ext_modules=[Extension('chopthin',['chopthin.cpp'],
                             include_dirs=[numpy.get_include()]
                         )],
      classifiers = ['Topic :: Scientific/Engineering :: Mathematics',
                     'Development Status :: 3 - Alpha'],
      license="GPLv3"
)
