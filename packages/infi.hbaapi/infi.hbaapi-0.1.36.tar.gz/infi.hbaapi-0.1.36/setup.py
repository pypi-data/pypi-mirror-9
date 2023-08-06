
SETUP_INFO = dict(
    name = 'infi.hbaapi',
    version = '0.1.36',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.hbaapi',
    license = 'PSF',
    description = """cross-platform bindings to FC-HBA APIs on Windows and Linux""",
    long_description = """cross-platform bindings to FC-HBA APIs on Windows and Linux""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'infi.cwrap',
'infi.dtypes.wwn',
'infi.exceptools',
'infi.instruct',
'infi.os_info',
'munch',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['hbaapi_mock = infi.hbaapi.scripts:hbaapi_mock',
'hbaapi_real = infi.hbaapi.scripts:hbaapi_real',],
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

