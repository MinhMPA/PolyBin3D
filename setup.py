import os
import sys
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize
import numpy

package_basename = 'PolyBin3D'
package_dir = os.path.join(os.path.dirname(__file__), package_basename)
sys.path.insert(0, package_dir)


# Compile pyx files with C
modules = ['utils']
for module in modules:
    ext_modules = [
        Extension(
            name=f'PolyBin3D.cython.{module}',
            sources=[f'PolyBin3D/cython/{module}.pyx'],
            libraries=['mvec','m'],
            extra_compile_args=["-fopenmp","-O3", "-ffast-math", "-march=broadwell"],
            extra_link_args=["-fopenmp"],
            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
            include_dirs=[numpy.get_include()],
            )
    ]
    
setup(
    name=package_basename,
    packages=find_packages(),
    include_package_data=True,
    ext_modules=cythonize(ext_modules), # Compile Cython modules and include them in the package
)