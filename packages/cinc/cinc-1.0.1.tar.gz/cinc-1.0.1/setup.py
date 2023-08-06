from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class cpp11_build_ext(build_ext):
    def build_extension(self, ext):
        if self.compiler.compiler_type != 'msvc':
            ext.extra_compile_args = ['-std=c++11']
        super().build_extension(ext)


with open('README.rst') as f:
    readme = f.read()

setup(
    name='cinc',
    version='1.0.1',
    description='Fast fixed-sized C-like integer types.',
    long_description=readme,
    url='https://pypi.python.org/pypi/cinc',
    author='Zacrath',
    author_email='zacrath@users.sf.net',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    ext_modules=[Extension('cinc', ['cinc.cpp'])],
    test_suite='testcases',
    cmdclass = {'build_ext': cpp11_build_ext},
    )
