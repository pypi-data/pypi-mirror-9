# This file is part of fedmsg.
# Copyright (C) 2014 Red Hat, Inc.
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
""" Tests for github2fedmsg messages """

import os
import unittest

from fedmsg_meta_fedora_infrastructure.tests.base import Base

from common import add_doc

full_patch1 = """From 404a417299f85eadb72457e94c08ac8ba39d53e8 Mon Sep 17 00:00:00 2001
From: Ralph Bean <rbean@redhat.com>
Date: Tue, 18 Mar 2014 13:45:12 -0400
Subject: [PATCH] Updates to the README.

---
 README.rst | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)

diff --git a/README.rst b/README.rst
index 34f7858..0bd925a 100644
--- a/README.rst
+++ b/README.rst
@@ -33,8 +33,8 @@ Using `virtualenvwrapper <pypi.python.org/pypi/virtualenvwrapper>`_::
   $ python setup.py develop
 
 Go off and `register your development application with github
-<https://github.com/settings/applications>`_.  Save the oauth tokens and add the
-secret one to a new file you create called ``secret.ini``.  Use the example
+<https://github.com/settings/applications>`_.  Save the oauth tokens and add
+the secret one to a new file you create called ``secret.ini``.  Use the example
 ``secret.ini.example`` file.
 
 
@@ -46,4 +46,4 @@ Create the database::
 Now, start the webapp::
 
   $ workon github2fedmsg
-  $ pserve development.ini
+  $ pserve development.ini --reload
"""


class TestGithubWebhook(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **enables a new
    repository for fedmsg broadcast**.  It, unfortunately, contains very little
    information.
    """

    expected_title = "github.webhook"
    expected_subti = 'A new github repository has been added to fedmsg'
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = expected_icon
    expected_packages = set([])
    expected_usernames = set([])
    expected_objects = set([])

    msg = {
        "username": "root",
        "i": 1,
        "timestamp": 1395167225,
        "msg_id": "2014-185bc51e-ad8e-4906-a623-445f3dbe794a",
        "topic": "org.fedoraproject.prod.github.webhook",
        "msg": {
            "hook_id": 1966604,
            "zen": "Responsive is better than fast.",
            "fas_usernames": {}
        }
    }


class TestGithubPush(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **pushes to a
    so-enabled github repository**.
    """

    expected_title = "github.push"
    expected_subti = 'ralph pushed 1 commit(s) to fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg/" + \
        "compare/60a6d3eb508c...404a417299f8"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/tree/README.rst'
    ])

    msg = {
        "username": "apache",
        "i": 1,
        "timestamp": 1395164717,
        "msg_id": "2014-f00946a5-2e26-4638-aa9f-ab3dffd9b4c2",
        "topic": "org.fedoraproject.prod.github.push",
        "msg": {
            "fas_usernames": {
                "ralphbean": "ralph",
            },
            "forced": False,
            "compare": "https://github.com/fedora-infra/github2fedmsg/" +
            "compare/60a6d3eb508c...404a417299f8",
            "after": "404a417299f85eadb72457e94c08ac8ba39d53e8",
            "repository": {
                "fork": False,
                "has_wiki": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "language": "Python",
                "has_downloads": True,
                "url": "https://github.com/fedora-infra/github2fedmsg",
                "master_branch": "develop",
                "created_at": 1395065396,
                "private": False,
                "name": "github2fedmsg",
                "pushed_at": 1395164716,
                "open_issues": 0,
                "watchers": 2,
                "has_issues": True,
                "owner": {
                    "email": None,
                    "name": "fedora-infra"
                },
                "organization": "fedora-infra",
                "forks": 0,
                "stargazers": 2,
                "id": 17830164,
                "size": 804
            },
            "created": False,
            "deleted": False,
            "commits": [
                {
                    "committer": {
                        "username": "ralphbean",
                        "email": "rbean@redhat.com",
                        "name": "Ralph Bean"
                    },
                    "added": [],
                    "author": {
                        "username": "ralphbean",
                        "email": "rbean@redhat.com",
                        "name": "Ralph Bean"
                    },
                    "distinct": True,
                    "timestamp": "2014-03-18T13:45:12-04:00",
                    "modified": [
                        "README.rst"
                    ],
                    "url": "https://github.com/fedora-infra/github2fedmsg/"
                    "commit/404a417299f85eadb72457e94c08ac8ba39d53e8",
                    "message": "Updates to the README.",
                    "removed": [],
                    "id": "404a417299f85eadb72457e94c08ac8ba39d53e8"
                }
            ],
            "pusher": {
                "email": "ralph.bean@gmail.com",
                "name": "ralphbean"
            },
            "head_commit": {
                "committer": {
                    "username": "ralphbean",
                    "email": "rbean@redhat.com",
                    "name": "Ralph Bean"
                },
                "added": [],
                "author": {
                    "username": "ralphbean",
                    "email": "rbean@redhat.com",
                    "name": "Ralph Bean"
                },
                "distinct": True,
                "timestamp": "2014-03-18T13:45:12-04:00",
                "modified": [
                    "README.rst"
                ],
                "url": "https://github.com/fedora-infra/github2fedmsg/"
                "commit/404a417299f85eadb72457e94c08ac8ba39d53e8",
                "message": "Updates to the README.",
                "removed": [],
                "id": "404a417299f85eadb72457e94c08ac8ba39d53e8"
            },
            "ref": "refs/heads/develop",
            "before": "60a6d3eb508ca45a0740de90628abf5b59c0e698"
        }
    }


class TestGithubIssue(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **changes an issue
    on an enabled github repository**.  This includes closing, opening,
    re-opening issues.

    Here's an example of re-opening:
    """

    expected_title = "github.issue.reopened"
    expected_subti = 'ralph reopened issue #3 on fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg/issues/3"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/issues/3',
    ])
    msg = {
        "username": "root",
        "i": 2,
        "timestamp": 1395166113,
        "msg_id": "2014-cbf1c4bc-6e87-47d2-8421-3f415b247781",
        "topic": "org.fedoraproject.dev.github.issue.reopened",
        "msg": {
            "action": "reopened",
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "issue": {
                "body": "Testing stuff.",
                "number": 3,
                "title": "Testing",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg/issues/3",
                "created_at": "2014-03-17T20:48:13Z",
                "labels": [],
                "updated_at": "2014-03-18T18:08:32Z",
                "comments": 4,
                "html_url": "https://github.com/fedora-infra/"
                "github2fedmsg/issues/3",
                "assignee": None,
                "state": "open",
                "user": {
                    "url": "https://api.github.com/users/ralphbean",
                    "html_url": "https://github.com/ralphbean",
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "site_admin": False,
                    "login": "ralphbean",
                    "type": "User",
                    "id": 331338,
                },
                "milestone": None,
                "closed_at": None,
                "pull_request": {
                    "html_url": None,
                },
                "id": 29597314
            },
            "sender": {
                "url": "https://api.github.com/users/ralphbean",
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "site_admin": False,
                "login": "ralphbean",
                "type": "User",
                "id": 331338,
            },
            "repository": {
                "has_wiki": False,
                "updated_at": "2014-03-18T17:45:15Z",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "site_admin": False,
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637,
                },
                "full_name": "fedora-infra/github2fedmsg",
                "id": 17830164,
                "size": 804,
                "has_downloads": True,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "open_issues": 1,
                "private": False,
                "forks_count": 0,
                "has_issues": True,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T17:45:16Z",
                "default_branch": "develop",
            }
        }
    }


class TestGithubIssueComment(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **comment on an
    issue on an enabled github repository**.
    """

    expected_title = "github.issue.comment"
    expected_subti = 'ralph commented on issue #3 on ' + \
        'fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg/" + \
        "issues/3#issuecomment-37971221"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/issues/3',
    ])
    msg = {
        "username": "root",
        "i": 1,
        "timestamp": 1395167817,
        "msg_id": "2014-573a1443-bb14-4891-bf6a-120827d8f24c",
        "topic": "org.fedoraproject.dev.github.issue.comment",
        "msg": {
            "comment": {
                "body": "This issue is super great!",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg/issues/comments/37971221",
                "created_at": "2014-03-18T18:36:56Z",
                "html_url": "https://github.com/fedora-infra/"
                "github2fedmsg/issues/3#issuecomment-37971221",
                "updated_at": "2014-03-18T18:36:56Z",
                "user": {
                    "url": "https://api.github.com/users/ralphbean",
                    "site_admin": False,
                    "html_url": "https://github.com/ralphbean",
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "login": "ralphbean",
                    "type": "User",
                    "id": 331338
                },
                "id": 37971221
            },
            "sender": {
                "url": "https://api.github.com/users/ralphbean",
                "site_admin": False,
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "login": "ralphbean",
                "type": "User",
                "id": 331338
            },
            "repository": {
                "has_wiki": False,
                "forks_count": 0,
                "updated_at": "2014-03-18T18:36:30Z",
                "private": False,
                "full_name": "fedora-infra/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 17830164,
                "size": 804,
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "has_issues": True,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T18:36:30Z",
                "open_issues": 1
            },
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "action": "created",
            "issue": {
                "body": "Testing stuff.",
                "number": 3,
                "title": "Testing",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg/issues/3",
                "created_at": "2014-03-17T20:48:13Z",
                "labels": [],
                "updated_at": "2014-03-18T18:36:56Z",
                "comments": 6,
                "html_url": "https://github.com/fedora-infra/"
                "github2fedmsg/issues/3",
                "assignee": None,
                "state": "open",
                "user": {
                    "url": "https://api.github.com/users/ralphbean",
                    "site_admin": False,
                    "html_url": "https://github.com/ralphbean",
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "login": "ralphbean",
                    "type": "User",
                    "id": 331338
                },
                "milestone": None,
                "closed_at": None,
                "pull_request": {
                    "html_url": None
                },
                "id": 29597314
            }
        }
    }


class TestGithubCreate(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **creates a new tag
    or branch**.
    """

    expected_title = "github.create"
    expected_subti = 'ralph created a new branch "feature/testing-stuff" ' + \
        'at fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/branch/feature/testing-stuff',
    ])
    msg = {
        "username": "root",
        "i": 1,
        "timestamp": 1395168693,
        "msg_id": "2014-eed312f7-7bb2-471c-acb6-afaaf8f097ba",
        "topic": "org.fedoraproject.dev.github.create",
        "msg": {
            "sender": {
                "url": "https://api.github.com/users/ralphbean",
                "site_admin": False,
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "login": "ralphbean",
                "type": "User",
                "id": 331338
            },
            "repository": {
                "has_wiki": False,
                "forks_count": 0,
                "updated_at": "2014-03-18T18:36:30Z",
                "private": False,
                "full_name": "fedora-infra/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 17830164,
                "size": 804,
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "has_issues": True,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T18:51:32Z",
                "open_issues": 1
            },
            "ref": "feature/testing-stuff",
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "ref_type": "branch",
            "pusher_type": "user",
            "master_branch": "develop",
            "description": "A pubsubhubbub application that rebroadcasts "
            "github events on the fedmsg bus"
        }
    }


class TestGithubPullRequestClosed(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **closes an existing
    pull request**.  There are similar messages for opening one.
    """

    expected_title = "github.pull_request.closed"
    expected_subti = 'ralph closed pull request #6 ' + \
        'on fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg/pull/6"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/pull/6',
    ])
    msg = {
        "username": "root",
        "i": 1,
        "timestamp": 1395169657,
        "msg_id": "2014-0ebb72ca-bc13-493e-9b1b-687d94ff11e3",
        "topic": "org.fedoraproject.dev.github.pull_request.closed",
        "msg": {
            "sender": {
                "url": "https://api.github.com/users/ralphbean",
                "site_admin": False,
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "login": "ralphbean",
                "type": "User",
                "id": 331338
            },
            "repository": {
                "has_wiki": False,
                "forks_count": 0,
                "updated_at": "2014-03-18T19:07:35Z",
                "private": False,
                "full_name": "fedora-infra/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 17830164,
                "size": 804,
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "has_issues": True,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T19:07:22Z",
                "open_issues": 1
            },
            "number": 6,
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "pull_request": {
                "body": "This is just a test.",
                "merge_commit_sha": "8b5898c780f41baf41de624fd47988b29ac42ecb",
                "updated_at": "2014-03-18T19:07:35Z",
                "assignee": None,
                "mergeable": None,
                "closed_at": "2014-03-18T19:07:35Z",
                "additions": 2,
                "id": 13701851,
                "title": "No more retask.",
                "comments": 0,
                "merged_at": None,
                "state": "closed",
                "changed_files": 1,
                "merged": False,
                "deletions": 2,
                "head": {
                    "repo": {
                        "has_wiki": False,
                        "forks_count": 0,
                        "updated_at": "2014-03-18T19:07:35Z",
                        "private": False,
                        "full_name": "fedora-infra/github2fedmsg",
                        "owner": {
                            "url": "https://api.github.com/users/fedora-infra",
                            "site_admin": False,
                            "html_url": "https://github.com/fedora-infra",
                            "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                            "login": "fedora-infra",
                            "type": "Organization",
                            "id": 3316637
                        },
                        "id": 17830164,
                        "size": 804,
                        "watchers_count": 2,
                        "stargazers_count": 2,
                        "homepage": None,
                        "fork": False,
                        "description": "A pubsubhubbub application that "
                        "rebroadcasts github events on the fedmsg bus",
                        "has_downloads": True,
                        "default_branch": "develop",
                        "html_url": "https://github.com/fedora-infra/"
                        "github2fedmsg",
                        "has_issues": True,
                        "master_branch": "develop",
                        "forks": 0,
                        "open_issues_count": 1,
                        "watchers": 2,
                        "name": "github2fedmsg",
                        "language": "Python",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "github2fedmsg",
                        "created_at": "2014-03-17T14:09:56Z",
                        "pushed_at": "2014-03-18T19:07:22Z",
                        "open_issues": 1
                    },
                    "sha": "54c80f816ed992a3a43c823e11cfce0a69f64d6d",
                    "ref": "feature/no-more-retask",
                    "user": {
                        "url": "https://api.github.com/users/fedora-infra",
                        "site_admin": False,
                        "html_url": "https://github.com/fedora-infra",
                        "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                        "login": "fedora-infra",
                        "type": "Organization",
                        "id": 3316637
                    },
                    "label": "fedora-infra:feature/no-more-retask"
                },
                "commits": 1,
                "html_url": "https://github.com/fedora-infra/"
                "github2fedmsg/pull/6",
                "number": 6,
                "base": {
                    "repo": {
                        "has_wiki": False,
                        "forks_count": 0,
                        "updated_at": "2014-03-18T19:07:35Z",
                        "private": False,
                        "full_name": "fedora-infra/github2fedmsg",
                        "owner": {
                            "url": "https://api.github.com/users/fedora-infra",
                            "site_admin": False,
                            "html_url": "https://github.com/fedora-infra",
                            "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                            "login": "fedora-infra",
                            "type": "Organization",
                            "id": 3316637
                        },
                        "id": 17830164,
                        "size": 804,
                        "watchers_count": 2,
                        "stargazers_count": 2,
                        "homepage": None,
                        "fork": False,
                        "description": "A pubsubhubbub application that "
                        "rebroadcasts github events on the fedmsg bus",
                        "has_downloads": True,
                        "default_branch": "develop",
                        "html_url": "https://github.com/fedora-infra/"
                        "github2fedmsg",
                        "has_issues": True,
                        "master_branch": "develop",
                        "forks": 0,
                        "open_issues_count": 1,
                        "watchers": 2,
                        "name": "github2fedmsg",
                        "language": "Python",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "github2fedmsg",
                        "created_at": "2014-03-17T14:09:56Z",
                        "pushed_at": "2014-03-18T19:07:22Z",
                        "open_issues": 1
                    },
                    "sha": "e6ee4b6d136e3897c00b6904becc29bacfa139e8",
                    "ref": "develop",
                    "user": {
                        "url": "https://api.github.com/users/fedora-infra",
                        "site_admin": False,
                        "html_url": "https://github.com/fedora-infra",
                        "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                        "login": "fedora-infra",
                        "type": "Organization",
                        "id": 3316637
                    },
                    "label": "fedora-infra:develop"
                },
                "user": {
                    "url": "https://api.github.com/users/ralphbean",
                    "site_admin": False,
                    "html_url": "https://github.com/ralphbean",
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "login": "ralphbean",
                    "type": "User",
                    "id": 331338
                },
                "milestone": None,
                "merged_by": None,
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg/pulls/6",
                "mergeable_state": "unknown",
                "created_at": "2014-03-18T19:05:44Z",
                "review_comments": 0
            },
            "action": "closed"
        }
    }


class TestGithubFork(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **forks a repo**.
    """

    expected_title = "github.fork"
    expected_subti = 'kushal124 forked fedora-infra/github2fedmsg'
    expected_link = "https://github.com/kushal124/github2fedmsg"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "00d52f5621a5f8b703b3054b2fac8b563c5ab3ff87a123ca1ce3f4b5e4a85f81"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set([])
    expected_objects = set([
        'fedora-infra/github2fedmsg/forks/kushal124',
    ])
    msg = {
        "username": "root",
        "i": 2,
        "timestamp": 1395170248,
        "msg_id": "2014-8134c58d-fe22-4296-ada9-047e4156a29a",
        "topic": "org.fedoraproject.dev.github.fork",
        "msg": {
            "forkee": {
                "has_wiki": False,
                "forks_count": 0,
                "updated_at": "2014-03-18T19:17:12Z",
                "private": False,
                "full_name": "kushal124/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/kushal124",
                    "site_admin": False,
                    "html_url": "https://github.com/kushal124",
                    "gravatar_id": "c53aaf0b0f0633d6d82571b92985b6f3",
                    "login": "kushal124",
                    "type": "User",
                    "id": 871398
                },
                "id": 17878694,
                "size": 804,
                "watchers_count": 0,
                "stargazers_count": 0,
                "homepage": None,
                "public": True,
                "fork": True,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/kushal124/github2fedmsg",
                "has_issues": False,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 0,
                "watchers": 0,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/kushal124/github2fedmsg",
                "created_at": "2014-03-18T19:17:28Z",
                "pushed_at": "2014-03-18T19:17:12Z",
                "open_issues": 0
            },
            "fas_usernames": {},
            "repository": {
                "has_wiki": False,
                "forks_count": 1,
                "updated_at": "2014-03-18T19:17:12Z",
                "private": False,
                "full_name": "fedora-infra/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 17830164,
                "size": 804,
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "has_issues": True,
                "master_branch": "develop",
                "forks": 1,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T19:17:12Z",
                "open_issues": 1
            },
            "sender": {
                "url": "https://api.github.com/users/kushal124",
                "site_admin": False,
                "html_url": "https://github.com/kushal124",
                "gravatar_id": "c53aaf0b0f0633d6d82571b92985b6f3",
                "login": "kushal124",
                "type": "User",
                "id": 871398
            }
        }
    }


class TestGithubStatus(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever a **continuous integration
    service updates the status of a new commit**.
    """

    expected_title = "github.status"
    expected_subti = 'PEP8Bot scan pending for fedora-infra/datanommer ' + \
        'e71e2ba9'
    expected_link = "http://pep8.me/fedora-infra/datanommer/commits" + \
        "/e71e2ba93fa992d9026f89d65f9220d5234bfab1"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/datanommer/status/'
        'e71e2ba93fa992d9026f89d65f9220d5234bfab1',
    ])
    msg = {
        "i": 1,
        "msg": {
            "branches": [
                {
                    "commit": {
                        "sha": "e2ebf193a204cedefb48bb8c67a000b44a3b05b9",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "datanommer/commits/"
                        "e2ebf193a204cedefb48bb8c67a000b44a3b05b9"
                    },
                    "name": "feature/fix-category-bug"
                }
            ],
            "commit": {
                "author": {
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "html_url": "https://github.com/ralphbean",
                    "id": 331338,
                    "login": "ralphbean",
                    "site_admin": False,
                    "type": "User",
                    "url": "https://api.github.com/users/ralphbean"
                },
                "commit": {
                    "author": {
                        "date": "2014-06-18T22:23:17Z",
                        "email": "rbean@redhat.com",
                        "name": "Ralph Bean"
                    },
                    "comment_count": 0,
                    "committer": {
                        "date": "2014-06-18T22:23:17Z",
                        "email": "rbean@redhat.com",
                        "name": "Ralph Bean"
                    },
                    "message": "Add failing test.",
                    "tree": {
                        "sha": "4087c0707f6e8c084c9dd4d61dd08f88ed948488",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "datanommer/git/trees/"
                        "4087c0707f6e8c084c9dd4d61dd08f88ed948488"
                    },
                    "url": "https://api.github.com/repos/fedora-infra/"
                    "datanommer/git/commits/"
                    "e71e2ba93fa992d9026f89d65f9220d5234bfab1"
                },
                "committer": {
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "html_url": "https://github.com/ralphbean",
                    "id": 331338,
                    "login": "ralphbean",
                    "site_admin": False,
                    "type": "User",
                    "url": "https://api.github.com/users/ralphbean"
                },
                "html_url": "https://github.com/fedora-infra/datanommer/"
                "commit/e71e2ba93fa992d9026f89d65f9220d5234bfab1",
                "parents": [
                    {
                        "html_url": "https://github.com/fedora-infra/"
                        "datanommer/commit/"
                        "03fd8eaedf5cb4ed5bc2ced77805f8c78bc7ccc9",
                        "sha": "03fd8eaedf5cb4ed5bc2ced77805f8c78bc7ccc9",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "datanommer/commits/"
                        "03fd8eaedf5cb4ed5bc2ced77805f8c78bc7ccc9"
                    }
                ],
                "sha": "e71e2ba93fa992d9026f89d65f9220d5234bfab1",
                "url": "https://api.github.com/repos/fedora-infra/datanommer/"
                "commits/e71e2ba93fa992d9026f89d65f9220d5234bfab1"
            },
            "context": "default",
            "target_url":  "http://pep8.me/fedora-infra/datanommer/commits"
            "/e71e2ba93fa992d9026f89d65f9220d5234bfab1",
            "description": "PEP8Bot scan pending",
            "fas_usernames": {'ralphbean': 'ralph'},
            "name": "fedora-infra/datanommer",
            "repository": {
                "created_at": "2012-07-05T18:07:29Z",
                "default_branch": "develop",
                "description": "Put all the messages in the postgres",
                "fork": False,
                "forks": 5,
                "forks_count": 5,
                "full_name": "fedora-infra/datanommer",
                "has_downloads": True,
                "has_issues": True,
                "has_wiki": False,
                "homepage": "",
                "html_url": "https://github.com/fedora-infra/datanommer",
                "id": 4912314,
                "language": "Python",
                "name": "datanommer",
                "open_issues": 0,
                "open_issues_count": 0,
                "owner": {
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "html_url": "https://github.com/fedora-infra",
                    "id": 3316637,
                    "login": "fedora-infra",
                    "site_admin": False,
                    "type": "Organization",
                    "url": "https://api.github.com/users/fedora-infra"
                },
                "private": False,
                "pushed_at": "2014-06-18T22:24:15Z",
                "size": 3304,
                "stargazers_count": 8,
                "updated_at": "2014-06-18T22:24:11Z",
                "url": "https://api.github.com/repos/fedora-infra/datanommer",
                "watchers": 8,
                "watchers_count": 8
            },
            "sender": {
                "gravatar_id": "b8083eb4cd5c69b1b1e9305bf2495d76",
                "html_url": "https://github.com/yograterol",
                "id": 3322886,
                "login": "yograterol",
                "site_admin": False,
                "type": "User",
                "url": "https://api.github.com/users/yograterol"
            },
            "sha": "e71e2ba93fa992d9026f89d65f9220d5234bfab1",
            "state": "pending"
        },
        "msg_id": "2014-8347add9-960c-4780-814a-c85378cd79bc",
        "source_name": "datanommer",
        "source_version": "0.6.4",
        "timestamp": 1403130257.0,
        "topic": "org.fedoraproject.prod.github.status"
    }


class TestGithubDelete(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **deletes a new tag
    or branch**.
    """

    expected_title = "github.delete"
    expected_subti = 'ralph deleted the "feature/testing-stuff" branch ' + \
        'at fedora-infra/github2fedmsg'
    expected_link = "https://github.com/fedora-infra/github2fedmsg"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/github2fedmsg/branch/feature/testing-stuff',
    ])
    msg = {
        "username": "root",
        "i": 1,
        "timestamp": 1395168693,
        "msg_id": "2014-eed312f7-7bb2-471c-acb6-afaaf8f097ba",
        "topic": "org.fedoraproject.dev.github.delete",
        "msg": {
            "sender": {
                "url": "https://api.github.com/users/ralphbean",
                "site_admin": False,
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "login": "ralphbean",
                "type": "User",
                "id": 331338
            },
            "repository": {
                "has_wiki": False,
                "forks_count": 0,
                "updated_at": "2014-03-18T18:36:30Z",
                "private": False,
                "full_name": "fedora-infra/github2fedmsg",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 17830164,
                "size": 804,
                "watchers_count": 2,
                "stargazers_count": 2,
                "homepage": None,
                "fork": False,
                "description": "A pubsubhubbub application that rebroadcasts "
                "github events on the fedmsg bus",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/github2fedmsg",
                "has_issues": True,
                "master_branch": "develop",
                "forks": 0,
                "open_issues_count": 1,
                "watchers": 2,
                "name": "github2fedmsg",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "github2fedmsg",
                "created_at": "2014-03-17T14:09:56Z",
                "pushed_at": "2014-03-18T18:51:32Z",
                "open_issues": 1
            },
            "ref": "feature/testing-stuff",
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "ref_type": "branch",
            "pusher_type": "user",
            "master_branch": "develop",
            "description": "A pubsubhubbub application that rebroadcasts "
            "github events on the fedmsg bus"
        }
    }


class TestGithubPullRequestComment(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **comments on a pull
    request**.
    """

    expected_title = "github.pull_request_review_comment"
    expected_subti = 'pingou commented on PR #129 on fedora-infra/fedocal'
    expected_link = "https://github.com/fedora-infra/fedocal/" + \
        "pull/129#discussion_r13957675"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "01fe73d687f4db328da1183f2a1b5b22962ca9d9c50f0728aafeac974856311c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['pingou'])
    expected_objects = set([
        'fedora-infra/fedocal/pull/129',
    ])
    msg = {
        "i": 4,
        "msg": {
            "action": "created",
            "comment": {
                "body": "I was thinking the ``flask.request.args.get(...",
                "commit_id": "31b3d03951c9cc40e4c497e09ff9b7c6f708239d",
                "created_at": "2014-06-19T08:30:17Z",
                "diff_hunk": "@@ -401,6 +401,19 @@ def calendar_list(...",
                "html_url": "https://github.com/fedora-infra/"
                "fedocal/pull/129#discussion_r13957675",
                "id": 13957675,
                "original_commit_id": "31b3d03951c9cc40e4c497e09ff9b7c6f"
                "708239d",
                "original_position": 16,
                "path": "fedocal/__init__.py",
                "position": 16,
                "updated_at": "2014-06-19T08:30:17Z",
                "url": "https://api.github.com/repos/fedora-infra/"
                "fedocal/pulls/comments/13957675",
                "user": {
                    "gravatar_id": "072b4416fbfad867a44bc7a5be5eddb9",
                    "html_url": "https://github.com/pypingou",
                    "id": 1240038,
                    "login": "pypingou",
                    "site_admin": False,
                    "type": "User",
                    "url": "https://api.github.com/users/pypingou"
                }
            },
            "fas_usernames": {'pypingou': 'pingou'},
            "pull_request": {
                "assignee": None,
                "base": {
                    "label": "fedora-infra:master",
                    "ref": "master",
                    "repo": {
                        "created_at": "2013-03-22T19:35:10Z",
                        "default_branch": "master",
                        "description": "A web based calendar application "
                        "for Fedora",
                        "fork": False,
                        "forks": 9,
                        "forks_count": 9,
                        "full_name": "fedora-infra/fedocal",
                        "has_downloads": True,
                        "has_issues": False,
                        "has_wiki": False,
                        "homepage": "",
                        "html_url": "https://github.com/fedora-infra/fedocal",
                        "id": 8959394,
                        "language": "Python",
                        "name": "fedocal",
                        "open_issues": 1,
                        "open_issues_count": 1,
                        "owner": {
                            "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                            "html_url": "https://github.com/fedora-infra",
                            "id": 3316637,
                            "login": "fedora-infra",
                            "site_admin": False,
                            "type": "Organization",
                            "url": "https://api.github.com/users/fedora-infra"
                        },
                        "private": False,
                        "pushed_at": "2014-06-19T08:24:38Z",
                        "size": 5719,
                        "stargazers_count": 4,
                        "updated_at": "2014-06-19T08:24:34Z",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "fedocal",
                        "watchers": 4,
                        "watchers_count": 4
                    },
                    "sha": "c7bdf86b8bd52c78805ee708ca11e2b81f90b82e",
                    "user": {
                        "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                        "html_url": "https://github.com/fedora-infra",
                        "id": 3316637,
                        "login": "fedora-infra",
                        "site_admin": False,
                        "type": "Organization",
                        "url": "https://api.github.com/users/fedora-infra"
                    }
                },
                "body": "This implement filtering the meetings in the list "
                "view server side rather than iterating through all the "
                "meetings retrieved",
                "closed_at": None,
                "created_at": "2014-06-17T10:16:31Z",
                "head": {
                    "label": "fedora-infra:filter_db",
                    "ref": "filter_db",
                    "repo": {
                        "created_at": "2013-03-22T19:35:10Z",
                        "default_branch": "master",
                        "description": "A web based calendar application for "
                        "Fedora",
                        "fork": False,
                        "forks": 9,
                        "forks_count": 9,
                        "full_name": "fedora-infra/fedocal",
                        "has_downloads": True,
                        "has_issues": False,
                        "has_wiki": False,
                        "homepage": "",
                        "html_url": "https://github.com/fedora-infra/fedocal",
                        "id": 8959394,
                        "language": "Python",
                        "name": "fedocal",
                        "open_issues": 1,
                        "open_issues_count": 1,
                        "owner": {
                            "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                            "html_url": "https://github.com/fedora-infra",
                            "id": 3316637,
                            "login": "fedora-infra",
                            "site_admin": False,
                            "type": "Organization",
                            "url": "https://api.github.com/users/fedora-infra"
                        },
                        "private": False,
                        "pushed_at": "2014-06-19T08:24:38Z",
                        "size": 5719,
                        "stargazers_count": 4,
                        "updated_at": "2014-06-19T08:24:34Z",
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "fedocal",
                        "watchers": 4,
                        "watchers_count": 4
                    },
                    "sha": "31b3d03951c9cc40e4c497e09ff9b7c6f708239d",
                    "user": {
                        "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                        "html_url": "https://github.com/fedora-infra",
                        "id": 3316637,
                        "login": "fedora-infra",
                        "site_admin": False,
                        "type": "Organization",
                        "url": "https://api.github.com/users/fedora-infra"
                    }
                },
                "html_url": "https://github.com/fedora-infra/fedocal/pull/129",
                "id": 17226690,
                "merge_commit_sha": "88cdeaf8e6986c4469f1619229c2b0580b0018dd",
                "merged_at": None,
                "milestone": None,
                "number": 129,
                "state": "open",
                "title": "Filter db",
                "updated_at": "2014-06-19T08:30:17Z",
                "url": "https://api.github.com/repos/fedora-infra/fedocal/"
                "pulls/129",
                "user": {
                    "gravatar_id": "072b4416fbfad867a44bc7a5be5eddb9",
                    "html_url": "https://github.com/pypingou",
                    "id": 1240038,
                    "login": "pypingou",
                    "site_admin": False,
                    "type": "User",
                    "url": "https://api.github.com/users/pypingou"
                }
            },
            "repository": {
                "created_at": "2013-03-22T19:35:10Z",
                "default_branch": "master",
                "description": "A web based calendar application for Fedora",
                "fork": False,
                "forks": 9,
                "forks_count": 9,
                "full_name": "fedora-infra/fedocal",
                "has_downloads": True,
                "has_issues": False,
                "has_wiki": False,
                "homepage": "",
                "html_url": "https://github.com/fedora-infra/fedocal",
                "id": 8959394,
                "language": "Python",
                "name": "fedocal",
                "open_issues": 1,
                "open_issues_count": 1,
                "owner": {
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "html_url": "https://github.com/fedora-infra",
                    "id": 3316637,
                    "login": "fedora-infra",
                    "site_admin": False,
                    "type": "Organization",
                    "url": "https://api.github.com/users/fedora-infra"
                },
                "private": False,
                "pushed_at": "2014-06-19T08:24:38Z",
                "size": 5719,
                "stargazers_count": 4,
                "updated_at": "2014-06-19T08:24:34Z",
                "url": "https://api.github.com/repos/fedora-infra/fedocal",
                "watchers": 4,
                "watchers_count": 4
            },
            "sender": {
                "gravatar_id": "072b4416fbfad867a44bc7a5be5eddb9",
                "html_url": "https://github.com/pypingou",
                "id": 1240038,
                "login": "pypingou",
                "site_admin": False,
                "type": "User",
                "url": "https://api.github.com/users/pypingou"
            }
        },
        "msg_id": "2014-cdf3f751-1af5-4773-91e4-6b2f71e0a905",
        "source_name": "datanommer",
        "source_version": "0.6.4",
        "timestamp": 1403166618.0,
        "topic": "org.fedoraproject.prod.github.pull_request_review_comment"
    }


class TestGithubCommitComment(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **comments directly
    on a commit**.
    """

    expected_title = "github.commit_comment"
    expected_subti = "ralph commented on a commit on fedora-infra/bodhi"
    expected_link = "https://github.com/fedora-infra/bodhi/commit/" + \
        "425c3610e129138a8b918b1eb1a40d291da20dc5" + \
        "#commitcomment-6733053"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set([
        'fedora-infra/bodhi/tree/bodhi/tests/functional/base.py',
    ])

    msg = {
        "i": 5,
        "msg": {
            "comment": {
                "body": "Maybe add a ``# comment`` here that 'BUILD_ID' "
                "is from jenkins and link to http://da.gd/QuQs ?",
                "commit_id": "425c3610e129138a8b918b1eb1a40d291da20dc5",
                "created_at": "2014-06-19T15:15:22Z",
                "html_url": "https://github.com/fedora-infra/bodhi/commit/"
                "425c3610e129138a8b918b1eb1a40d291da20dc5"
                "#commitcomment-6733053",
                "id": 6733053,
                "line": 46,
                "path": "bodhi/tests/functional/base.py",
                "position": 21,
                "updated_at": "2014-06-19T15:15:22Z",
                "url": "https://api.github.com/repos/fedora-infra/bodhi/"
                "comments/6733053",
                "user": {
                    "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                    "html_url": "https://github.com/ralphbean",
                    "id": 331338,
                    "login": "ralphbean",
                    "site_admin": False,
                    "type": "User",
                    "url": "https://api.github.com/users/ralphbean"
                }
            },
            "fas_usernames": {
                "ralphbean": "ralph"
            },
            "repository": {
                "created_at": "2009-02-06T19:38:10Z",
                "default_branch": "pyramid",
                "description": "Bodhi is a web-system that facilitates the "
                "process of publishing updates for a Fedora-based software "
                "distribution.",
                "fork": False,
                "forks": 11,
                "forks_count": 11,
                "full_name": "fedora-infra/bodhi",
                "has_downloads": True,
                "has_issues": True,
                "has_wiki": True,
                "homepage": "http://bodhi.fedorahosted.org",
                "html_url": "https://github.com/fedora-infra/bodhi",
                "id": 123299,
                "language": "Python",
                "name": "bodhi",
                "open_issues": 14,
                "open_issues_count": 14,
                "owner": {
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "html_url": "https://github.com/fedora-infra",
                    "id": 3316637,
                    "login": "fedora-infra",
                    "site_admin": False,
                    "type": "Organization",
                    "url": "https://api.github.com/users/fedora-infra"
                },
                "private": False,
                "pushed_at": "2014-06-19T07:11:03Z",
                "size": 34892,
                "stargazers_count": 8,
                "updated_at": "2014-06-19T07:11:03Z",
                "url": "https://api.github.com/repos/fedora-infra/bodhi",
                "watchers": 8,
                "watchers_count": 8
            },
            "sender": {
                "gravatar_id": "ba940b433c2695635d32d2c4aec00540",
                "html_url": "https://github.com/ralphbean",
                "id": 331338,
                "login": "ralphbean",
                "site_admin": False,
                "type": "User",
                "url": "https://api.github.com/users/ralphbean"
            }
        },
        "msg_id": "2014-dacff065-b47b-4d0b-9dc3-86406f6be9fb",
        "source_name": "datanommer",
        "source_version": "0.6.4",
        "timestamp": 1403190922.0,
        "topic": "org.fedoraproject.prod.github.commit_comment"
    }


class TestGithubLegacyWatch(Base):
    """ Old github.watch messages.  These no longer exist. """

    expected_title = "github.watch"
    expected_subti = "alikins started watching fedora-infra/summershum"
    expected_link = "https://github.com/fedora-infra/summershum/watchers"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "d23ffcf6c375ae6351f54b6d4e381c6910e68d666370e5ff21e4322cd56690bf"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set([])
    expected_objects = set([
        'fedora-infra/summershum/watchers',
    ])
    msg = {
        "source_name": "datanommer",
        "i": 1,
        "timestamp": 1403363334.0,
        "msg_id": "2014-5273bf43-d483-48d4-a8d6-11c988cae0cb",
        "topic": "org.fedoraproject.prod.github.watch",
        "source_version": "0.6.4",
        "msg": {
            "action": "started",
            "fas_usernames": {},
            "repository": {
                "has_wiki": False,
                "forks_count": 7,
                "updated_at": "2014-06-21T15:08:53Z",
                "private": False,
                "full_name": "fedora-infra/summershum",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 16620564,
                "size": 907,
                "watchers_count": 10,
                "forks": 7,
                "homepage": "",
                "fork": False,
                "description": "fedmsg consumer that extracts hashes of "
                "source files",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/summershum",
                "has_issues": True,
                "stargazers_count": 10,
                "open_issues_count": 2,
                "watchers": 10,
                "name": "summershum",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/summershum",
                "created_at": "2014-02-07T16:35:59Z",
                "pushed_at": "2014-06-13T12:11:18Z",
                "open_issues": 2
            },
            "sender": {
                "url": "https://api.github.com/users/alikins",
                "site_admin": False,
                "html_url": "https://github.com/alikins",
                "gravatar_id": "81877b32b5fac41db3207c94ecc26173",
                "login": "alikins",
                "type": "User",
                "id": 15162
            }
        }
    }


class TestGithubStar(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **stars a
    repository**.
    """

    expected_title = "github.star"
    expected_subti = "alikins starred fedora-infra/summershum"
    expected_link = "https://github.com/fedora-infra/summershum/stargazers"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "d23ffcf6c375ae6351f54b6d4e381c6910e68d666370e5ff21e4322cd56690bf"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set([])
    expected_objects = set([
        'fedora-infra/summershum/stargazers',
    ])
    msg = {
        "source_name": "datanommer",
        "i": 1,
        "timestamp": 1403363334.0,
        "msg_id": "2014-5273bf43-d483-48d4-a8d6-11c988cae0cb",
        "topic": "org.fedoraproject.prod.github.star",
        "source_version": "0.6.4",
        "msg": {
            "action": "started",
            "fas_usernames": {},
            "repository": {
                "has_wiki": False,
                "forks_count": 7,
                "updated_at": "2014-06-21T15:08:53Z",
                "private": False,
                "full_name": "fedora-infra/summershum",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "ebdef1eaaa4b1c1cb01f5570efbb3cc4",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 16620564,
                "size": 907,
                "watchers_count": 10,
                "forks": 7,
                "homepage": "",
                "fork": False,
                "description": "fedmsg consumer that extracts hashes of "
                "source files",
                "has_downloads": True,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/summershum",
                "has_issues": True,
                "stargazers_count": 10,
                "open_issues_count": 2,
                "watchers": 10,
                "name": "summershum",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/summershum",
                "created_at": "2014-02-07T16:35:59Z",
                "pushed_at": "2014-06-13T12:11:18Z",
                "open_issues": 2
            },
            "sender": {
                "url": "https://api.github.com/users/alikins",
                "site_admin": False,
                "html_url": "https://github.com/alikins",
                "gravatar_id": "81877b32b5fac41db3207c94ecc26173",
                "login": "alikins",
                "type": "User",
                "id": 15162
            }
        }
    }


class TestGithubRelease(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **releases a new
    tarball**.
    """
    expected_title = "github.release"
    expected_subti = "lmacken cut a release of fedmsg-notify, version 0.5.5"
    expected_link = "https://github.com/fedora-infra/fedmsg-notify/" + \
        "releases/tag/0.5.5"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "203f6cb95b44b5d38aa21425b066dd522d3e19d8919cf4b339f29e0ea7f03e9b"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['lmacken'])
    expected_objects = set(['fedora-infra/fedmsg-notify/releases/0.5.5'])
    msg = {
        "source_name": "datanommer",
        "i": 2,
        "timestamp": 1418844844.0,
        "msg_id": "2014-2db6e3e6-4eca-42cf-8057-d2c75946360d",
        "topic": "org.fedoraproject.prod.github.release",
        "source_version": "0.6.4",
        "msg": {
            "sender": {
                "url": "https://api.github.com/users/lmacken",
                "site_admin": False,
                "html_url": "https://github.com/lmacken",
                "gravatar_id": "",
                "login": "lmacken",
                "type": "User",
                "id": 9980
            },
            "repository": {
                "has_wiki": True,
                "has_pages": False,
                "updated_at": "2014-12-17T19:31:57Z",
                "private": False,
                "full_name": "fedora-infra/fedmsg-notify",
                "owner": {
                    "url": "https://api.github.com/users/fedora-infra",
                    "site_admin": False,
                    "html_url": "https://github.com/fedora-infra",
                    "gravatar_id": "",
                    "login": "fedora-infra",
                    "type": "Organization",
                    "id": 3316637
                },
                "id": 7964139,
                "size": 408,
                "watchers_count": 10,
                "forks": 5,
                "homepage": "http://lewk.org/blog/fedmsg-notify",
                "fork": False,
                "description": "Fedmsg Desktop Notifications",
                "has_downloads": True,
                "forks_count": 5,
                "default_branch": "develop",
                "html_url": "https://github.com/fedora-infra/fedmsg-notify",
                "has_issues": True,
                "stargazers_count": 10,
                "open_issues_count": 7,
                "watchers": 10,
                "name": "fedmsg-notify",
                "language": "Python",
                "url": "https://api.github.com/repos/fedora-infra/"
                "fedmsg-notify",
                "created_at": "2013-02-01T18:54:35Z",
                "pushed_at": "2014-12-17T19:32:09Z",
                "open_issues": 7
            },
            "fas_usernames": {
                "fedora-infra": "github_org_fedora-infra",
                "lmacken": "lmacken"
            },
            "release": {
                "body": "* Make the topic grid scrollable (rhbz#1087076)\r\n* "
                "Fixed the distro-specific imports\r\n* Uses the abrt python "
                "API",
                "tag_name": "0.5.5",
                "assets": [
                    {
                        "name": "fedmsg-notify-0.5.5.tar.bz2",
                        "updated_at": "2014-12-17T19:34:07Z",
                        "created_at": "2014-12-17T19:34:06Z",
                        "browser_download_url": "https://github.com/fedora"
                        "-infra/fedmsg-notify/releases/download/0.5.5/fedmsg"
                        "-notify-0.5.5.tar.bz2",
                        "label": None,
                        "url": "https://api.github.com/repos/fedora-infra/"
                        "fedmsg-notify/releases/assets/348355",
                        "state": "uploaded",
                        "content_type": "application/x-bzip",
                        "download_count": 0,
                        "uploader": {
                            "following_url": "https://api.github.com/users/"
                            "lmacken/following{/other_user}",
                            "gists_url": "https://api.github.com/users/"
                            "lmacken/gists{/gist_id}",
                            "organizations_url": "https://api.github.com/"
                            "users/lmacken/orgs",
                            "url": "https://api.github.com/users/lmacken",
                            "events_url": "https://api.github.com/"
                            "users/lmacken/events{/privacy}",
                            "html_url": "https://github.com/lmacken",
                            "subscriptions_url": "https://api.github.com/"
                            "users/lmacken/subscriptions",
                            "avatar_url": "https://avatars.githubusercontent."
                            "com/u/9980?v=3",
                            "repos_url": "https://api.github.com/"
                            "users/lmacken/repos",
                            "received_events_url": "https://api.github.com/"
                            "users/lmacken/received_events",
                            "gravatar_id": "",
                            "starred_url": "https://api.github.com/"
                            "users/lmacken/starred{/owner}{/repo}",
                            "site_admin": False,
                            "login": "lmacken",
                            "type": "User",
                            "id": 9980,
                            "followers_url": "https://api.github.com/"
                            "users/lmacken/followers"
                        },
                        "id": 348355,
                        "size": 21147
                    }
                ],
                "author": {
                    "url": "https://api.github.com/users/lmacken",
                    "site_admin": False,
                    "html_url": "https://github.com/lmacken",
                    "gravatar_id": "",
                    "login": "lmacken",
                    "type": "User",
                    "id": 9980
                },
                "url": "https://api.github.com/repos/fedora-infra/fedmsg"
                "-notify/releases/791850",
                "created_at": "2014-12-17T19:30:32Z",
                "target_commitish": "develop",
                "html_url": "https://github.com/fedora-infra/fedmsg"
                "-notify/releases/tag/0.5.5",
                "published_at": "2014-12-17T19:34:14Z",
                "draft": False,
                "prerelease": False,
                "id": 791850,
                "name": "0.5.5 release"
            },
            "action": "published",
            "organization": {
                "url": "https://api.github.com/orgs/fedora-infra",
                "login": "fedora-infra",
                "id": 3316637
            }
        }
    }

class TestGithubPageBuild(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **builds a Github Page**.
    """
    expected_title = "github.page_build"
    expected_subti = "codeblock rebuilt the github.io page for fedora-infra/fas3-api-haskell"
    expected_link = "http://fedora-infra.github.io/fas3-api-haskell/"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "eef5c0a84876858ad15b1d90c299ce281cc9bdfa04971fc6d35c60ffa5463853"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['codeblock'])
    expected_objects = set(['fedora-infra/fas3-api-haskell/page_build'])
    msg = {
        "source_name": "datanommer",
        "i": 2,
        "timestamp": 1421345410.0,
        "msg_id": "2015-d6548647-adac-46e4-bdd3-ad8c1d7b1d8c",
        "topic": "org.fedoraproject.prod.github.page_build",
        "source_version": "0.6.4",
        "msg": {
            "sender": {
              "url": "https://api.github.com/users/relrod", 
              "site_admin": False, 
              "html_url": "https://github.com/relrod", 
              "gravatar_id": "", 
              "login": "relrod", 
              "type": "User", 
              "id": 43930
            }, 
            "repository": {
              "has_wiki": True, 
              "has_pages": True, 
              "updated_at": "2015-01-15T18:13:37Z", 
              "private": False, 
              "full_name": "fedora-infra/fas3-api-haskell", 
              "owner": {
                "url": "https://api.github.com/users/fedora-infra", 
                "site_admin": False, 
                "html_url": "https://github.com/fedora-infra", 
                "gravatar_id": "", 
                "login": "fedora-infra", 
                "type": "Organization", 
                "id": 3316637
                }, 
              "id": 29308328, 
              "size": 0, 
              "watchers_count": 0, 
              "forks": 0, 
              "homepage": "https://relrod.github.io/fas3", 
              "fork": False, 
              "description": "Haskell API bindings for the upcoming Fedora Accounts System v3", 
              "has_downloads": True, 
              "forks_count": 0, 
              "default_branch": "master", 
              "html_url": "https://github.com/fedora-infra/fas3-api-haskell", 
              "has_issues": True, 
              "stargazers_count": 0, 
              "open_issues_count": 0, 
              "watchers": 0, 
              "name": "fas3-api-haskell", 
              "language": "Shell", 
              "url": "https://api.github.com/repos/fedora-infra/fas3-api-haskell", 
              "created_at": "2015-01-15T17:12:50Z", 
              "pushed_at": "2015-01-15T17:13:15Z", 
              "open_issues": 0
            }, 
            "fas_usernames": {
              "fedora-infra": "github_org_fedora-infra", 
              "relrod": "codeblock"
            }, 
            "build": {
              "status": "built", 
              "pusher": {
                "url": "https://api.github.com/users/relrod", 
                "site_admin": False, 
                "html_url": "https://github.com/relrod", 
                "gravatar_id": "", 
                "login": "relrod", 
                "type": "User", 
                "id": 43930
              }, 
              "url": "https://api.github.com/repos/fedora-infra/fas3-api-haskell/pages/builds/12773963", 
              "created_at": "2015-01-15T18:13:38Z", 
              "updated_at": "2015-01-15T18:13:41Z", 
              "error": {
                "message": None
              }, 
              "duration": 3718, 
              "commit": "670613e19f0b41beb837554b9be84959ccd7085e"
            }, 
            "organization": {
              "url": "https://api.github.com/orgs/fedora-infra", 
              "login": "fedora-infra", 
              "description": None, 
              "id": 3316637
            }, 
            "id": 12773963
        }
    }

class TestGithubTeamAdd(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **Adds a team to Github Repository**.
    """
    expected_title = "github.team_add"
    expected_subti = "The 'owners' team was added to the fedora-infra/fas3-api-haskell repository"
    expected_link = "https://github.com/fedora-infra/fas3-api-haskell"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "7e8ab7d8f1d6b28321cd145cae04c92220b5eae0f77266009b12bebdbd4dd613"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set([])
    expected_objects = set(['fedora-infra/fas3-api-haskell/team_add'])
    msg = {
        "source_name": "datanommer",
        "i": 1,
        "timestamp": 1421345406.0,
        "msg_id": "2015-b24f3067-26ae-4df9-b35e-95b19b77fe73",
        "topic": "org.fedoraproject.prod.github.team_add",
        "source_version": "0.6.4",
        "msg": {
        "organization": {
          "url": "https://api.github.com/orgs/fedora-infra", 
          "login": "fedora-infra", 
          "description": None, 
          "id": 3316637
        }, 
        "team": {
          "description": None, 
          "permission": "admin", 
          "url": "https://api.github.com/teams/319263", 
          "id": 319263, 
          "slug": "owners", 
          "name": "Owners"
        }, 
        "fas_usernames": {
          "fedora-infra": "github_org_fedora-infra"
        }, 
        "repository": {
          "has_wiki": True, 
          "has_pages": True, 
          "updated_at": "2015-01-15T18:13:37Z", 
          "private": False, 
          "full_name": "fedora-infra/fas3-api-haskell", 
          "owner": {
            "url": "https://api.github.com/users/fedora-infra", 
            "site_admin": False, 
            "html_url": "https://github.com/fedora-infra", 
            "gravatar_id": "", 
            "login": "fedora-infra", 
            "type": "Organization", 
            "id": 3316637
          }, 
          "id": 29308328, 
          "size": 0, 
          "watchers_count": 0, 
          "forks": 0, 
          "homepage": "https://relrod.github.io/fas3", 
          "fork": False, 
          "description": "Haskell API bindings for the upcoming Fedora Accounts System v3", 
          "has_downloads": True, 
          "forks_count": 0, 
          "default_branch": "master", 
          "html_url": "https://github.com/fedora-infra/fas3-api-haskell", 
          "has_issues": True, 
          "stargazers_count": 0, 
          "open_issues_count": 0, 
          "watchers": 0, 
          "name": "fas3-api-haskell", 
          "language": "Shell", 
          "url": "https://api.github.com/repos/fedora-infra/fas3-api-haskell", 
          "created_at": "2015-01-15T17:12:50Z", 
          "pushed_at": "2015-01-15T17:13:15Z", 
          "open_issues": 0
        }, 
        "sender": {
          "url": "https://api.github.com/users/fedora-infra", 
          "site_admin": False, 
          "html_url": "https://github.com/fedora-infra", 
          "gravatar_id": "", 
          "login": "fedora-infra", 
          "type": "Organization", 
          "id": 3316637
        }
      }
    }

class TestGithubMember(Base):
    """ There exists `a service
    <https://apps.fedoraproject.org/github2fedmsg>`_ to link the select github
    repos of fedora contributors with the fedmsg bus.

    Messages of *this* type are published whenever someone **Adds a team to Github Repository**.
    """
    expected_title = "github.member"
    expected_subti = "ralph added decause as a member of ralphbean/lightsaber"
    expected_link = "https://github.com/ralphbean/lightsaber"
    expected_icon = "https://apps.fedoraproject.org/img/icons/github.png"
    expected_secondary_icon = (
        "https://seccdn.libravatar.org/avatar/"
        "9c9f7784935381befc302fe3c814f9136e7a33953d0318761669b8643f4df55c"
        "?s=64&d=retro")
    expected_packages = set([])
    expected_usernames = set(['ralph'])
    expected_objects = set(['ralphbean/lightsaber/member'])
    msg = {
        "source_name": "datanommer",
        "i": 2,
        "timestamp": 1426257201.0,
        "msg_id": "2015-b21fdc03-9f22-4d6f-a086-74d4dae25b6c",
        "topic": "org.fedoraproject.prod.github.member",
        "source_version": "0.6.4",
        "msg": {
            "action": "added",
            "member": {
              "url": "https://api.github.com/users/decause",
              "site_admin": False,
              "html_url": "https://github.com/decause",
              "gravatar_id": "",
              "login": "decause",
              "type": "User",
              "id": 427420
            },
            "fas_usernames": {
              "ralphbean": "ralph"
            },
            "repository": {
              "has_wiki": False,
              "has_pages": False,
              "updated_at": "2015-03-13T13:23:31Z",
              "private": False,
              "full_name": "ralphbean/lightsaber",
              "owner": {
                "url": "https://api.github.com/users/ralphbean",
                "site_admin": False,
                "html_url": "https://github.com/ralphbean",
                "gravatar_id": "",
                "login": "ralphbean",
                "type": "User",
                "id": 331338
              },
              "id": 13132894,
              "size": 1397,
              "watchers_count": 15,
              "forks": 3,
              "homepage": "",
              "fork": False,
              "description": "Everyone has to build their own...",
              "has_downloads": True,
              "forks_count": 3,
              "default_branch": "develop",
              "html_url": "https://github.com/ralphbean/lightsaber",
              "has_issues": True,
              "stargazers_count": 15,
              "open_issues_count": 1,
              "watchers": 15,
              "name": "lightsaber",
              "language": "Python",
              "url": "https://api.github.com/repos/ralphbean/lightsaber",
              "created_at": "2013-09-26T20:00:13Z",
              "pushed_at": "2015-03-13T13:23:31Z",
              "open_issues": 1
            },
            "sender": {
              "url": "https://api.github.com/users/ralphbean",
              "site_admin": False,
              "html_url": "https://github.com/ralphbean",
              "gravatar_id": "",
              "login": "ralphbean",
              "type": "User",
              "id": 331338
            }
        }
    }


if not 'FEDMSG_META_NO_NETWORK' in os.environ:
    TestGithubPush.expected_long_form = full_patch1
    TestGithubIssue.expected_long_form = "Testing stuff."
    TestGithubIssueComment.expected_long_form = "This issue is super great!"
    TestGithubPullRequestComment.expected_long_form = \
        "I was thinking the ``flask.request.args.get(..."
    TestGithubCommitComment.expected_long_form = \
        "Maybe add a ``# comment`` here that 'BUILD_ID' " + \
        "is from jenkins and link to http://da.gd/QuQs ?"


add_doc(locals())

if __name__ == '__main__':
    unittest.main()
