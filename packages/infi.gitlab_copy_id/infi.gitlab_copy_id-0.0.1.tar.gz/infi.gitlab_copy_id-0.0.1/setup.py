
SETUP_INFO = dict(
    name = 'infi.gitlab_copy_id',
    version = '0.0.1',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://git.infinidat.com/host-opensource/infi.gitlab_copy_id',
    license = 'PSF',
    description = """A script like ssh-copy-id, only that copies it to GitLab""",
    long_description = """A script like ssh-copy-id, only that copies it to GitLab""",

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
'dnspython',
'docopt',
'json_rest',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'gitlab-copy-id = infi.gitlab_copy_id:main'
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

