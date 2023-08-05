from setuptools.extension import Extension

import sys
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__


SETUP_INFO = dict(
    name = 'infi.tracing',
    version = '0.2.9',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.tracing',
    license = 'PSF',
    description = """short description here""",
    long_description = """long description here""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['cython',
'greenlet',
'infi.pyutils',
'setuptools'],
    setup_requires = ['setuptools_cython'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['*.pxd', '*.h', 'greenlet.h', '*.hpp', '*.pyx']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        ),

)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')


def build_ext_modules():
    from platform import platform, system
    extra_compile_args = []
    extra_link_args = []
    if platform().startswith("Darwin-13"):
        extra_compile_args += ["-stdlib=libstdc++"]
        extra_link_args += ["-stdlib=libstdc++"]
    if system() in ["Linux", "Darwin"]:
        extra_compile_args += ["-Wno-format-security", "-Wno-strict-prototypes"]
        platform_specific_sources = ["src/mintsystem/gcc/datetime.c", "src/mintsystem/gcc/mutex.c",
                                     "src/mintsystem/gcc/semaphore.c", "src/mintsystem/gcc/timer.c"]
    else:
        platform_specific_sources = ["src/mintsystem/msvc/datetime.c", "src/mintsystem/msvc/thread.c",
                                     "src/mintsystem/msvc/timer.c"]
    return [Extension("infi.tracing.ctracing",
               language="c++",
               sources=["src/infi/tracing/ctracing.pyx", "src/infi/tracing/thread_storage.cpp",
                        "src/infi/tracing/trace_dump.cpp", "src/infi/tracing/wait_and_ensure_exit.cpp",
                        "src/mintomic/mintomic_gcc.c"] + platform_specific_sources,
               include_dirs=["src/infi/tracing", "src"],
               define_macros=[("_REENTRANT", 1)],
               libraries=[],
               extra_compile_args=extra_compile_args,
               extra_link_args=extra_link_args)]


def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['ext_modules'] = build_ext_modules()
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()
