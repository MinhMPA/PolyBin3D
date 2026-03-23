import os
import platform
import sys
from pathlib import Path
from ctypes.util import find_library

import numpy
from setuptools import Extension, setup
from Cython.Build import cythonize


def get_build_config():
    """Return platform-appropriate build settings for Cython extensions."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    include_dirs = [numpy.get_include()]
    libraries = []
    extra_compile_args = ["-O3", "-ffast-math"]
    extra_link_args = []

    # Linux-specific math libraries.
    # libmvec is glibc-specific and is not available on macOS.
    if system == "linux":
        libraries.extend(["mvec", "m"])
        extra_compile_args.append("-march=native")
        extra_compile_args.append("-fopenmp")
        extra_link_args.append("-fopenmp")

    elif system == "darwin":
        # Do not use x86-only flags on Apple Silicon.
        if machine in ("x86_64", "amd64"):
            extra_compile_args.append("-march=native")

        # OpenMP on macOS is optional and toolchain-dependent.
        conda_prefix = os.environ.get("CONDA_PREFIX", "")
        candidate_prefixes = [Path(conda_prefix)] if conda_prefix else []
        candidate_prefixes += [
            Path("/opt/homebrew/opt/libomp"),
            Path("/usr/local/opt/libomp"),
        ]

        omp_include = None
        omp_lib_dir = None
        for prefix in candidate_prefixes:
            include_dir = prefix / "include"
            lib_dir = prefix / "lib"
            if (include_dir / "omp.h").exists() and any(
                (lib_dir / name).exists() for name in ["libomp.dylib", "libomp.a"]
            ):
                omp_include = include_dir
                omp_lib_dir = lib_dir
                break

        if omp_include and omp_lib_dir:
            include_dirs.append(str(omp_include))
            extra_compile_args.extend(["-Xpreprocessor", "-fopenmp"])
            extra_link_args.extend([f"-L{omp_lib_dir}", "-lomp"])
        elif find_library("omp"):
            extra_compile_args.extend(["-Xpreprocessor", "-fopenmp"])
            extra_link_args.append("-lomp")
        else:
            print(
                "WARNING: OpenMP runtime not found on macOS; building without OpenMP.",
                file=sys.stderr,
            )

    else:
        # Conservative defaults for other Unix-like platforms.
        extra_compile_args.append("-march=native")

    return {
        "include_dirs": include_dirs,
        "libraries": libraries,
        "extra_compile_args": extra_compile_args,
        "extra_link_args": extra_link_args,
    }


build_cfg = get_build_config()

modules = ["utils"]
ext_modules = [
    Extension(
        name=f"PolyBin3D.cython.{module}",
        sources=[f"PolyBin3D/cython/{module}.pyx"],
        libraries=build_cfg["libraries"],
        extra_compile_args=build_cfg["extra_compile_args"],
        extra_link_args=build_cfg["extra_link_args"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        include_dirs=build_cfg["include_dirs"],
    )
    for module in modules
]

setup(
    ext_modules=cythonize(ext_modules),
)
