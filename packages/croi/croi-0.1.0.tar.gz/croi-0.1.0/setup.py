import os
from distutils.core import setup
from distutils.extension import Extension

setup_args = {
    'name': 'croi',
    'author': 'Daniel Collins',
    'author_email': 'dacjames@gmail.com',
    'description': 'A library of useful crosscutting python functions, classes, and generators.',
    'long_description': 'README.md',
    'license': 'MIT',
    'keywords': 'library lib util utility',
    'url': 'https://github.com/dacjames/croi',
    'version': '0.1.0',
    'packages': ['croi'],
}

try:
    from Cython.Build import cythonize
    use_cython = True

except ImportError:
    use_cython = False


submodules_names = [
    'generators',
    'decorators',
    'reflection',
    'collection'
]

if use_cython:
    ext_files = []
    for filename in submodules_names:
        pyx_file = os.path.join("croi", filename + ".pyx")
        py_file = os.path.join("croi", filename + ".py")

        if os.path.exists(pyx_file):
            ext_files.append(pyx_file)
        else:
            ext_files.append(py_file)

    setup_args['ext_modules'] = cythonize(ext_files)

else:
    setup_args['ext_modules'] = [
        Extension("croi." + filename, [os.path.join("croi", filename + ".c")])
        for filename in submodules_names
    ]

try:
    setup(**setup_args)

except:
    print 'Setup failed trying to build optimized version.  Using pure python.'
    del setup_args['ext_modules']
    setup(**setup_args)
