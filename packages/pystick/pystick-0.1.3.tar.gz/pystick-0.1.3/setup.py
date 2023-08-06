
SETUP_INFO = dict(
    name = 'pystick',
    version = '0.1.3',
    author = 'Tal Yalon',
    author_email = 'tal.yalon@gmail.com',

    url = 'https://infinigit.infinidat.com/host/pystick',
    license = 'PSF',
    description = """embeddable python for the masses""",
    long_description = """embeddable python for the masses""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['setuptools'],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': ['*.c',
'*.scons',
'*.win32',
'*.x86_64',
'SConscript',
'SConstruct']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['pack = pystick.pack:main'],
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

