
SETUP_INFO = dict(
    name = 'infi.wmi',
    version = '0.1.26.post4',
    author = 'Roey Darwish Dror',
    author_email = 'roeyd@infinidat.com',

    url = 'https://github.com/Infinidat/infi.wmi',
    license = 'PSF',
    description = """monkeypatched fork of comptypes to support faster WMI access""",
    long_description = """monkeypatched fork of comptypes to support faster WMI access""",

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

    install_requires = ['comtypes',
'setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
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
