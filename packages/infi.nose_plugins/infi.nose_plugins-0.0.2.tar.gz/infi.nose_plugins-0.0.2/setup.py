
SETUP_INFO = dict(
    name = 'infi.nose_plugins',
    version = '0.0.2',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://infinigit.infinidat.com/host/nose-plugins',
    license = 'PSF',
    description = """nose plugins""",
    long_description = """nose plugins""",

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
'lxml',
'nose',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        "console_scripts": [],
        "gui_scripts": [],
        "nose.plugins": ['logbook = infi.nose_plugins.logbook:LogbookPlugin',
                         'stderr = infi.nose_plugins.stderr:LoggingToStderrPlugin',
                         'html = infi.nose_plugins.html:NosePlugin',
                        ],
        },
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

