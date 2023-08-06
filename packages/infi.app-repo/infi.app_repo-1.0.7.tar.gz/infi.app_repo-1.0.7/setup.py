
SETUP_INFO = dict(
    name = 'infi.app_repo',
    version = '1.0.7',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.app_repo',
    license = 'PSF',
    description = """A user-friendly RPM/DEP repository""",
    long_description = """A user-friendly RPM/DEB repository""",

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
'docopt',
'Flask',
'Flask-AutoIndex',
'gevent',
'httpie',
'infi.docopt-completion',
'infi.execute',
'infi.gevent-utils',
'infi.logging',
'infi.pyutils',
'infi.rpc',
'infi.traceback',
'ipython',
'pyftpdlib',
'pygments',
'pysendfile',
'requests',
'schematics',
'setuptools',
'waiting',
'zc.buildout'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'*.css',
'*.html',
'*.ico',
'*.js',
'*.mako',
'*.png',
'*.sh',
'gpg_batch_file',
'nginx.conf',
'vsftpd.conf'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['app_repo = infi.app_repo.scripts:app_repo'],
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

