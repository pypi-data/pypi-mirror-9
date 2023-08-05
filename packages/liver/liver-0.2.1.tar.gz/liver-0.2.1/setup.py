from setuptools import setup, find_packages

version = "0.2.1"

long_description=""
try:
    long_description=file('README.md').read()
except Exception:
    pass

license=""
try:
    license=file('MIT_License.txt').read()
except Exception:
    pass

setup(
    name = 'liver',
    version = version,
    description = 'Video recorder',
    author = 'Pablo Saavedra',
    author_email = 'pablo.saavedra@interoud.com',
    url = 'http://github.com/psaavedra/liver',
    download_url= 'https://github.com/psaavedra/liver/zipball/master',
    packages = find_packages(),
    include_package_data=True,
    scripts=[
        "tools/",
        "tools/liver-delete-jobs",
        "tools/liver-delete-recordings",
        "tools/liver-do-jobs",
        "tools/liver-get-mo-to-delete",
        "tools/liver-mo-status"
    ],
    zip_safe=False,
    install_requires=[
        "django >=1.6, <1.7",
        "python-dateutil",
        "httplib2",
        "simplejson",
        "slugify",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
    ],
    long_description=long_description,
    license=license,
    keywords = "rule manager django liver recorder",
)
