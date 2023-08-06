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
    'version': '0.1.1',
    'packages': ['croi'],
}

try:
    from Cython.Build import cythonize
    use_cython = True

except ImportError:
    use_cython = False

force_cython = os.environ.get('FORCE_CYTHON', 'False').upper() == 'TRUE'

submodules_names = [
    'generators',
    'decorators',
    'reflection',
    'collection'
]

ext_info = []

for filename in submodules_names:
    pyx_file = os.path.join("croi", filename + ".pyx")
    py_file = os.path.join("croi", filename + ".py")
    c_file = os.path.join("croi", filename + ".c")

    if os.path.exists(pyx_file):
        if use_cython:
            ext_info.append((filename, pyx_file))
        else:
            ext_info.append((filename, c_file))
    elif force_cython:
        if use_cython:
            ext_info.append((filename, py_file))
        elif os.path.exists(c_file):
            ext_info.append((filename, c_file))

if use_cython:
    setup_args['ext_modules'] = cythonize([
        path for filename, path in ext_info
    ])

else:
    setup_args['ext_modules'] = [
        Extension("croi." + filename, [path])
        for filename, path in ext_info
    ]

try:
    setup(**setup_args)

except:
    print 'Setup failed trying to build optimized version.  Using pure python.'
    del setup_args['ext_modules']
    setup(**setup_args)
