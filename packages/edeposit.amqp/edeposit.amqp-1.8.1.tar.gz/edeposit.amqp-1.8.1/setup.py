#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import shutil

from setuptools import setup, find_packages
from distutils.command.sdist import sdist

try:
    from docs import getVersion
except ImportError:  # during packaging, docs are moved to html_docs
    from html_docs import getVersion


changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    changelog
])


class BuildSphinx(sdist):
    """
    Generates sphinx documentation, puts it into html_docs/, packs it to
    package and removes unused directory.
    """
    def run(self):
        d = os.path.abspath('.')
        DOCS = d + "/" + "docs"
        DOCS_IN = DOCS + "/build/html"
        DOCS_OUT = d + "/html_docs"

        if not self.dry_run:
            print "Generating the documentation .."

            os.chdir(DOCS)
            os.system("make clean")
            os.system("make html")

            if os.path.exists(DOCS_OUT):
                shutil.rmtree(DOCS_OUT)

            shutil.copytree(DOCS_IN, DOCS_OUT)
            shutil.copy(DOCS + "/__init__.py", DOCS_OUT)  # for getVersion()
            os.chdir(d)

        sdist.run(self)

        if os.path.exists(DOCS_OUT):
            shutil.rmtree(DOCS_OUT)


setup(
    name='edeposit.amqp',
    version=getVersion(changelog),
    description="E-Deposit's AMQP definitions and common classes/patterns.",
    long_description=long_description,
    url='https://github.com/edeposit/edeposit.amqp/',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='GPL2+',

    packages=find_packages(exclude=['ez_setup']),

    scripts=[
        "bin/edeposit_amqp_tool.py",
        "bin/edeposit_amqp_alephdaemon.py",
        "bin/edeposit_amqp_calibredaemon.py",
        "bin/edeposit_amqp_ftp_monitord.py",
        "bin/edeposit_amqp_ftp_managerd.py",
        "bin/edeposit_amqp_antivirusd.py",
        "bin/edeposit_amqp_harvester.py",
        "bin/edeposit_amqp_ltpd.py",
        "bin/edeposit_amqp_pdfgend.py"
    ],

    namespace_packages=['edeposit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        "python-daemon==1.6",
        "pika>=0.9.13",
        "sh",                # required by edeposit.amqp.ftp for monitor daemon
        "edeposit.amqp.aleph>=1.4.1",
        "edeposit.amqp.serializers>=1.1.1",
        "edeposit.amqp.calibre>=1.0.1",
        "edeposit.amqp.ftp>=0.6.4",
        "edeposit.amqp.antivirus>=1.0.0",
        "edeposit.amqp.harvester"
    ],
    extras_require={
        "test": [
            "pytest",
            "sh"
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },

    cmdclass={'sdist': BuildSphinx}
)
