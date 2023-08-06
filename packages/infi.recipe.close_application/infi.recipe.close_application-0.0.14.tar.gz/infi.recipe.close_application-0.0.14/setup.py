
SETUP_INFO = dict(
    name = 'infi.recipe.close_application',
    version = '0.0.14',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.recipe.close_application',
    license = 'PSF',
    description = """buildout recipe for terminating all executables""",
    long_description = """buildout recipe for terminating all executables""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['psutil>=2.0',
'setuptools',
'zc.buildout'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [],
        'gui_scripts': [],
        'zc.buildout': ['default = infi.recipe.close_application:CloseApplication']
        }
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

