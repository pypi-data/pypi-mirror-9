from __future__ import absolute_import
import subprocess

from setuptools import setup

try:
    pandoc = subprocess.Popen(['pandoc', 'README.md', '--to', 'rst'],
                              stdout=subprocess.PIPE)

    readme = str(pandoc.communicate()[0])

except OSError:
    with open('README.md') as f:
        readme = f.read()

setup(
    name="notedown",
    version="1.4.1",
    description="Convert markdown to IPython notebook.",
    long_description=readme,
    packages=['notedown'],
    author="Aaron O'Leary",
    author_email='dev@aaren.me',
    license='BSD 2-Clause',
    url='http://github.com/aaren/notedown',
    install_requires=['ipython[nbconvert] >= 3.0', 'pandoc-attributes', 'six'],
    entry_points={'console_scripts': ['notedown = notedown:cli', ]},
    package_dir={'notedown': 'notedown'},
    package_data={'notedown': ['templates/markdown.tpl']},
    include_package_data=True,
)
