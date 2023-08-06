
SETUP_INFO = dict(
    name = 'srm_client',
    version = '0.1.5',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://git.infinidat.com/host-opensource/infi.srm_client',
    license = 'PSF',
    description = """A simple client for VMWare SRM""",
    long_description = """A Python client for connecting to VMWare SRM via its SOAP API and performing recovery operations""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['colorama',
'docopt',
'infi.pyutils',
'infi.recipe.console_scripts',
'jinja2',
'requests',
'setuptools',
'tabulate',
'xmltodict'],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': ['srm_client/templates/*.xml']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['srm = srm_client.cli:srm'],
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

