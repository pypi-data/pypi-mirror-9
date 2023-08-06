from distutils.core import setup, Extension
from Cython.Distutils import build_ext

define_macros = [('VOID', 'int'),
                 ('REAL', 'double'),
                 ('NO_TIMER', 1),
                 ('TRILIBRARY', 1),
                 ('ANSI_DECLARATORS', 1)]

setup(name='triangle',
    packages=['triangle'],
    package_dir={'triangle':'triangle'},
    package_data={'triangle':['data/*.node',
                             'data/*.ele',
                             'data/*.poly',
                             'data/*.area',
                             'data/*.edge',
                             'data/*.neigh']},
    version='2015.03.28',
    description='Python binding to the triangle library',
    author='Dzhelil Rufat',
    author_email='drufat@caltech.edu',
    license='GNU LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    url='http://dzhelil.info/triangle',
    requires = ['numpy(>=1.7.0)', 'cython(>=0.18)'],
    cmdclass = {'build_ext': build_ext},
    ext_modules=[
                 Extension('triangle.core', ['c/triangle.c', 
                                             'triangle/c_triangle.pxd', 
                                             'triangle/core.pyx'],
                           include_dirs = ['c'],
                           define_macros = define_macros)
    ]
)
