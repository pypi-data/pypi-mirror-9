
SETUP_INFO = dict(
    name = 'infi.multipathtools',
    version = '0.1.29.post2',
    author = 'wiggin15',
    author_email = 'wiggin15@yahoo.com',

    url = 'https://github.com/Infinidat/infi.multipathtools',
    license = 'PSF',
    description = """python bindings to multipath-tools daemon""",
    long_description = """python bindings to multipath-tools daemon""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.exceptools',
'infi.execute',
'infi.instruct',
'infi.pyutils',
'munch',
'setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['*txt']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['print_maps = infi.multipathtools.scripts:print_maps', 'print_config = infi.multipathtools.scripts:print_config', 'print_model_examples = infi.multipathtools.model.scripts:print_examples'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()
