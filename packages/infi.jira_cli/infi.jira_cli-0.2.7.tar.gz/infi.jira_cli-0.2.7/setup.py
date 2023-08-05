
SETUP_INFO = dict(
    name = 'infi.jira_cli',
    version = '0.2.7',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.jira_cli',
    license = 'PSF',
    description = """JIRA command-line tools""",
    long_description = """JIRA command-line tools""",

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
'git-py',
'infi.docopt-completion',
'infi.execute',
'infi.pyutils',
'Jinja2',
'jira-python',
'munch',
'PrettyTable',
'schematics',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['jish.zsh']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'jirelease = infi.jira_cli.jirelease:main',
'jirelnotes = infi.jira_cli.jirelnotes:main',
'jish = infi.jira_cli.jish:main',
'jissue = infi.jira_cli.jissue:main'
],
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

