import os
from distutils.core import setup
from setuptools import find_packages

VERSION = __import__("xvarnish").VERSION
CLASSIFIERS = [
    'Programming Language :: Python :: 2.6',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]
install_requires = [
    'shortuuid==0.4.2',
    'netifaces==0.10.4',
    'argparse==1.3.0',
    'requests==2.5.1',
    'python-daemon==1.6.1',
]

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('xvarnish'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[12:] # Strip "admin_tools/" or "admin_tools\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))
setup(
    name="xvarnish-python",
    description="A Python package to include pip dependencies for xVarnish.",
    version=VERSION,
    author="Bryon Elston",
    author_email="bryon@x10hosting.com",
    url="http://xvarnish.com",
    download_url="http://staging.xvarnish.com/xvarnish-python-1.0.tar.gz",
    package_dir={'xvarnish': 'xvarnish'},
    packages=packages,
    package_data={'xvarnish': data_files},
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)