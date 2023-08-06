import os
from os.path import abspath, dirname, join, isfile
from setuptools import setup, find_packages, Command
from setuptools.command.register import register

import stored_settings as module

# Consts
README_MD = "README.md"
README_RST = "README.rst"

# Important vars
cur_dir = abspath(dirname(__file__))
readme_md = join(cur_dir, README_MD)
readme_rst = join(cur_dir, README_RST)

long_description = ""
using_rst = False
try:
    with open(readme_rst, 'r') as f:
        long_description = f.read()
        using_rst = True
except IOError:
    with open(readme_md, 'r') as f:
        long_description = f.read()


class GenerateRstCommand(Command):
    """Generate a README.rst file
    This file can be used after in the register command.
    """

    description = "generate a README.rst file from README.md"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        if isfile(readme_rst):
            os.remove(readme_rst)

    def run(self):
        import tempfile
        import shutil
        import pypandoc

        tmp_readme_md = join(tempfile.gettempdir(), README_MD)
        shutil.copy(readme_md, tmp_readme_md)
        try:
            # Now, convert to RST
            rst = pypandoc.convert(tmp_readme_md, "rst")
            with open(readme_rst, "w") as f:
                f.write(rst)

        finally:
            os.remove(tmp_readme_md)


class RegisterCommand(register):
    """Check if we're using README.rst before register in Pypi
    """

    def finalize_options(self):
        if not using_rst:
            raise Exception("{} file not found".format(README_RST))

        return register.finalize_options(self)


setup(
    name=module.__program__,
    version=module.__version__,
    description=module.__doc__,
    long_description=long_description,
    author=module.__author__,
    author_email=module.__email__,
    url='https://github.com/zvadim/django-stored-settings',
    download_url='https://github.com/zvadim/django-stored-settings/tarball/%s' % module.__version__,
    keywords=['django', 'settings', 'dynamic', 'stored'],
    packages=find_packages(include=('stored_settings',)),
    package_data={
        'stored_settings': [
            'templates/admin/stored_settings/settings/*.html',
        ],
    },

    requires=['django (>=1.3)', 'Pillow'],

    license='MIT license',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

    # Commands
    cmdclass={
        "generate_rst": GenerateRstCommand,
        "register": RegisterCommand,
    }
)