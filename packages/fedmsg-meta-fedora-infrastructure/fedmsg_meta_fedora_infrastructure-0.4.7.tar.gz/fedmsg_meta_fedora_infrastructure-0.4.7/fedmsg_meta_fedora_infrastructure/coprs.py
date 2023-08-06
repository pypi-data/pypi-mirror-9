# This file is part of fedmsg.
# Copyright (C) 2013-2014 Red Hat, Inc.
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

import copy

from fedmsg_meta_fedora_infrastructure import BaseProcessor
from fasshim import gravatar_url

_statuses = {
    0: 'failed',
    1: 'success',
    3: 'running',
    5: 'skipped',
}


_long_template = """Package:  {pkg}
COPR:     {owner}/{copr}
Built by: {user}
Status:   {status}
ID:       {build}

Logs:
  Build:     https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/{pkg}/build.log
  Root:      https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/{pkg}/root.log
  Copr:      https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/build-{build}.log
  Mockchain: https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/mockchain.log
Results:     https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/{pkg}/
Repodata:    https://copr-be.cloud.fedoraproject.org/results/{owner}/{copr}/{chroot}/repodata/
"""


class CoprsProcessor(BaseProcessor):
    __name__ = "Copr"
    __description__ = "the Cool Other Package Repositories system"
    __link__ = "https://copr-fe.cloud.fedoraproject.org"
    __docs__ = "https://fedorahosted.org/copr"
    __obj__ = "Extra Repository Updates"
    __icon__ = "https://apps.fedoraproject.org/img/icons/copr.png"

    def long_form(self, msg, **config):
        if 'copr.build.end' in msg['topic']:
            kwargs = copy.copy(msg['msg'])

            # For backwards compat with ancient messages
            if 'owner' not in kwargs:
                kwargs['owner'] = kwargs['user']

            kwargs['status'] = _statuses.get(kwargs.get('status'), 'unknown')

            details = _long_template.format(**kwargs)
            return details

    def subtitle(self, msg, **config):

        user = msg['msg'].get('user')
        copr = msg['msg'].get('copr')
        chroot = msg['msg'].get('chroot')
        pkg = msg['msg'].get('pkg')

        status = _statuses.get(msg['msg'].get('status'), 'unknown')

        if 'copr.build.start' in msg['topic']:
            tmpl = self._("{user} started a new build of the {copr} copr")
        elif 'copr.build.end' in msg['topic']:
            tmpl = self._(
                "{user}'s {copr} copr build of {pkg} for {chroot} "
                "finished with '{status}'")
        elif 'copr.chroot.start' in msg['topic']:
            tmpl = self._("{user}'s {copr} copr started a new {chroot} chroot")
        elif 'copr.worker.create' in msg['topic']:
            tmpl = self._("a new worker was created")
        else:
            raise NotImplementedError()

        return tmpl.format(user=user, copr=copr, pkg=pkg,
                           chroot=chroot, status=status)

    def link(self, msg, **config):
        user = msg['msg'].get('owner', msg['msg'].get('user'))
        copr = msg['msg'].get('copr')
        chroot = msg['msg'].get('chroot', None)
        build = msg['msg'].get('build')

        if 'chroot' in msg['topic']:
            tmpl = ("https://copr-be.cloud.fedoraproject.org/"
                    "results/{user}/{copr}/{chroot}/")
        elif 'build' in msg['topic']:
            tmpl = ("https://copr.fedoraproject.org/"
                    "coprs/{user}/{copr}/build/{build}/")
        else:
            return "https://copr.fedoraproject.org"

        return tmpl.format(user=user, copr=copr, chroot=chroot, build=build)

    def secondary_icon(self, msg, **config):
        if 'user' in msg['msg']:
            return gravatar_url(msg['msg']['user'])

    def usernames(self, msg, **config):
        usernames = set()
        if 'user' in msg['msg']:
            usernames.add(msg['msg']['user'])
        if 'owner' in msg['msg']:
            usernames.add(msg['msg']['owner'])
        return usernames

    def objects(self, msg, **config):
        items = ['coprs']

        if 'copr' in msg['msg']:
            items.append(msg['msg']['copr'])

        items.append('.'.join(msg['topic'].split('.')[-2:]))

        if 'chroot' in msg['topic']:
            items.append(msg['msg']['chroot'])

        return set(['/'.join(items)])
