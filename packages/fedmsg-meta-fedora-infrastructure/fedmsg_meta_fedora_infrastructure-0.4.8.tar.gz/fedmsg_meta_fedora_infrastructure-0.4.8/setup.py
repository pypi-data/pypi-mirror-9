# This file is part of fedmsg.
# Copyright (C) 2012-2014 Red Hat, Inc.
#
# fedmsg is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# fedmsg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>
#

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

# Ridiculous as it may seem, we need to import multiprocessing and
# logging here in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except Exception:
    pass


install_requires = [
    'fedmsg',
    'python-fedora',
    'python-dateutil',
]
tests_require = [
    'nose',
]

if sys.version_info < (2, 7):
    install_requires.extend([
        'argparse',
        'ordereddict',
    ])
    tests_require.extend([
        'unittest2',
    ])

entry_points = {
    'fedmsg.meta': [
        "askbot=fedmsg_meta_fedora_infrastructure.askbot:AskbotProcessor",
        "bodhi=fedmsg_meta_fedora_infrastructure.bodhi:BodhiProcessor",
        "scm=fedmsg_meta_fedora_infrastructure.scm:SCMProcessor",
        "tagger=fedmsg_meta_fedora_infrastructure.tagger:TaggerProcessor",
        "planet=fedmsg_meta_fedora_infrastructure.planet:PlanetProcessor",
        "bot=fedmsg_meta_fedora_infrastructure.supybot:SupybotProcessor",
        "wiki=fedmsg_meta_fedora_infrastructure.mediawiki:WikiProcessor",
        "fas=fedmsg_meta_fedora_infrastructure.fas:FASProcessor",
        "comp=fedmsg_meta_fedora_infrastructure.compose:ComposeProcessor",
        "pkgdb=fedmsg_meta_fedora_infrastructure.pkgdb:PkgdbProcessor",
        "buildsys="
        "fedmsg_meta_fedora_infrastructure.buildsys:KojiProcessor",
        "trac=fedmsg_meta_fedora_infrastructure.trac:TracProcessor",
        "mailman=fedmsg_meta_fedora_infrastructure.mailman3:MailmanProcessor",
        "fedbadges=fedmsg_meta_fedora_infrastructure.badges:BadgesProcessor",
        "ansible=fedmsg_meta_fedora_infrastructure.ansible:AnsibleProcessor",
        "datanommer=fedmsg_meta_fedora_infrastructure.datanommer:"
        "DatanommerProcessor",
        "nuancier=fedmsg_meta_fedora_infrastructure.nuancier:"
        "NuancierProcessor",
        "fedocal=fedmsg_meta_fedora_infrastructure.fedocal:FedocalProcessor",
        "coprs=fedmsg_meta_fedora_infrastructure.coprs:CoprsProcessor",
        "anitya=fedmsg_meta_fedora_infrastructure.anitya:"
        "AnityaProcessor",
        "summershum=fedmsg_meta_fedora_infrastructure.summershum:"
        "SummerShumProcessor",
        "jenkins=fedmsg_meta_fedora_infrastructure.jenkins:JenkinsProcessor",
        "github=fedmsg_meta_fedora_infrastructure.github:GithubProcessor",
        "bugzilla=fedmsg_meta_fedora_infrastructure.bz:BugzillaProcessor",
        "elections=fedmsg_meta_fedora_infrastructure.elections:"
        "ElectionsProcessor",
        "fmn=fedmsg_meta_fedora_infrastructure.fmn:FMNProcessor",
        "fedimg=fedmsg_meta_fedora_infrastructure.fedimg:FedimgProcessor",
        "kerneltest=fedmsg_meta_fedora_infrastructure.kerneltest:"
        "KernelTestProcessor",
        "koschei=fedmsg_meta_fedora_infrastructure.koschei:KoscheiProcessor",
        "hotness=fedmsg_meta_fedora_infrastructure.hotness:HotnessProcessor",
        "mm2=fedmsg_meta_fedora_infrastructure.mm2:MirrorManagerProcessor",
        "irc=fedmsg_meta_fedora_infrastructure.karma:KarmaProcessor",
        "pagure=fedmsg_meta_fedora_infrastructure.pagure:PagureProcessor",
    ]
}

setup(
    name='fedmsg_meta_fedora_infrastructure',
    version='0.4.8',
    description=
    "fedmsg metadata providers for Fedora Infrastructure's deployment",
    long_description=long_description,
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/ralphbean/fedmsg_meta_fedora_infrastructure/',
    license='LGPLv2+',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points=entry_points
)
