from distutils.core import setup
setup(
    name = 'rblwatch',
    packages = ['rblwatch'],
    scripts = ['bin/rblcheck', 'bin/rblwatch'],
    version = '0.2.2',
    description = 'RBL lookups with Python',
    author = 'James Polera',
    author_email = 'james@uncryptic.com',
    maintainer = 'Thomas Merkel',
    maintainer_email = 'tm@core.io',
    url = 'https://github.com/drscream/rblwatch',
    keywords = ['rbl', 'blacklist', 'mail'],
    install_requires = [
        'IPy == 0.81',
        'dnspython == 1.11.1',
    ],
)
