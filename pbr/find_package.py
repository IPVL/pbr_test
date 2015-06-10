__author__ = 'Hi'
import os

import setuptools

def smart_find_packages(package_list):
    packages = []
    for pkg in package_list.strip().split("\n"):
        pkg_path = pkg.replace('.', os.path.sep)
        packages.append(pkg)
        packages.extend(['%s.%s' % (pkg, f) for f in setuptools.find_packages(pkg_path)])
    return "\n".join(set(packages))
