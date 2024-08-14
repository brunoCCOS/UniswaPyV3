from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

ext_modules = [
    Extension(
        "UniswaPyV3",
        ["./uniswapyv3/utils.py"],
    )
]

setup(ext_modules=cythonize(ext_modules),
    script_args=['build_ext', '--inplace'],
)
