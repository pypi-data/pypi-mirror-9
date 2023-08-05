#! /usr/bin/env python
# coding: utf-8
# Copyright Ruamel bvba 2007-2014

from __future__ import print_function

import sys
import os
from textwrap import dedent

name_space = 'ruamel'
package_name = 'argparse'
full_package_name = name_space + '.std.' + package_name

exclude_files = [
    'setup.py',
]

if __name__ == '__main__':
    # put here so setup.py can be imported more easily
    from setuptools import setup, find_packages, Extension
    from setuptools.command import install_lib


# < from ruamel.util.new.setupinc import get_version, _check_convert_version
def get_version():
    v_i = 'version_info = '
    for line in open('__init__.py'):
        if not line.startswith(v_i):
            continue
        s_e = line[len(v_i):].strip()[1:-1].split(', ')
        elems = [x.strip()[1:-1] if x[0] in '\'"' else int(x) for x in s_e]
        break
    return elems


def _check_convert_version(tup):
    """create a PEP 386 pseudo-format conformant string from tuple tup"""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    nr_digits = 0  # nr of adjacent digits in rest, to verify
    post_dev = False  # are we processig post/dev
    for x in tup[1:]:
        if isinstance(x, int):
            nr_digits += 1
            if nr_digits > 2:
                raise ValueError("to many consecutive digits " + ret_val)
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            if post_dev:
                raise ValueError("release level specified after "
                                 "post/dev:" + x)
            nr_digits = 0
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            nr_digits = 1  # only one can follow
            post_dev = True
            ret_val += '.post' if first_letter == 'p' else '.dev'
        else:
            raise ValueError('First letter of "' + x + '" not recognised')
    return ret_val


# < from ruamel.util.new.setupinc import version_info, version_str
version_info = get_version()
version_str = _check_convert_version(version_info)


# < from ruamel.util.new.setupinc import MyInstallLib
class MyInstallLib(install_lib.install_lib):
    "create __init__.py on the fly"
    def run(self):
        install_lib.install_lib.run(self)
        init_txt = dedent('''\
            # coding: utf-8
            # Copyright © 2013-2014 Anthon van der Neut, RUAMEL bvba
            "generated __init__.py "
            try:
                __import__('pkg_resources').declare_namespace(__name__)
            except ImportError:
                pass
        ''')
        init_path = full_package_name.split('.')[:-1]
        for product_init in [
            os.path.join(
                *([self.install_dir] + init_path[:p+1] + ['__init__.py']))
                for p in range(len(init_path))
        ]:
            if not os.path.exists(product_init):
                print('creating %s' % product_init)
                with open(product_init, "w") as fp:
                    fp.write(init_txt)
        setup = os.path.join(self.install_dir, 'setup.py')

    def install(self):
        fpp = full_package_name.split('.')  # full package path
        full_exclude_files = [os.path.join(*(fpp + [x]))
                              for x in exclude_files]
        alt_files = []
        outfiles = install_lib.install_lib.install(self)
        for x in outfiles:
            for full_exclude_file in full_exclude_files:
                if full_exclude_file in x:
                    os.remove(x)
                    break
            else:
                alt_files.append(x)
        return alt_files


# <


def main():
    install_requires = [
    ]
    if sys.version_info[:2] == (2, 6):
        install_requires.append("argparse")
    packages = [full_package_name] + [(full_package_name + '.' + x) for x
                                      in find_packages(exclude=['test'])]
    setup(
        name=full_package_name,
        version=version_str,
        description="Enhancements to argparse: extra actions, subparser "
        "aliases, smart formatter, a decorator based wrapper",
        install_requires=install_requires,
        long_description=open('README.rst').read(),
        url='https://bitbucket.org/ruamel/std.' + package_name,
        author='Anthon van der Neut',
        author_email='a.van.der.neut@ruamel.eu',
        license="MIT license",
        package_dir={full_package_name: '.'},
        namespace_packages=[name_space],
        packages=packages,
        cmdclass={'install_lib': MyInstallLib},
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ]
    )

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sdist':
        assert full_package_name == os.path.abspath(os.path.dirname(
            __file__)).split('site-packages' + os.path.sep)[1].replace(
            os.path.sep, '.')
    main()
