#!/usr/bin/env python
"""
This program allows one to convert a Roundup issue tracker instance to Bitbucket's issue tracker.
Point it to the directory containing the database, and it will generate a ZIP-file which you can import from the
Bitbuckets issue tracker settings page.

Currently, the issues are converted, including the attached messages with their creation dates. All attached files
are also included and linked to the correct issues.

The history of changes of the states of issues, the title of issues is not preserved. Furthermore, timezones are not
taken into account.
"""
__author__ = 'Takis Issaris'
__email__ = 'takis@issaris.org'
__copyright__ = "Copyright 2015, Panagiotis Issaris"
__license__ = "GPL"

import argparse
import datetime
import json
import logging
import os
import sqlite3
import zipfile


def convert_date_format(old_date_format):
    """
    Converts the date from SQLite style 20150116162100.12312 to the format Bitbucket expects
    f.e. 2015-01-16T16:21:00.12312.

    # FIXME: Take timezones into account.

    :param old_date_format: The string based format SQLite returns for dates
    :return: The format expected by Bitbucket
    """
    new_date_format = datetime.datetime.strptime(old_date_format, '%Y%m%d%H%M%S.%f')
    return new_date_format.strftime("%Y-%m-%dT%H:%M:%S.%f%z")


class RoundupReader(object):
    users = {}
    statuses = {}
    priorities = {}

    def __init__(self):
        self.data = {
            'issues': [],
            'comments': [],
            'attachments': [],
            'logs': [],
            'meta': {
                'default_kind': 'bug'
            },
            'components': [],
            'milestones': [
                {
                    'name': 'M1'
                }
            ],
            'versions': [],
        }

    def convert_issues(self):
        """
        Read the issues from the SQlite database and put them in a list of dictionaries in the format
        Bitbucket expects.
        :return:
        """
        p2p = {
            'critical': ('bug', 'blocker'),
            'urgent': ('bug', 'critical'),
            'bug': ('bug', 'major'),
            'feature': ('enhancement', 'minor'),
            'wish': ('proposal', 'minor'),
        }

        s2s = {
            'unread': 'new',
            'deferred': 'on hold',
            'chatting': 'open',
            'need-eg': 'on hold',
            'in-progress': 'open',
            'testing': 'resolved',
            'done-cbb': 'resolved',
            'resolved': 'resolved',
        }

        self.nr_issues = 0
        query = "SELECT * FROM _ISSUE"
        for row in self.c.execute(query):
            self.nr_issues += 1
            activity, actor, assigned, creation, creator, priority, status, title, pk, retired = row

            pm = self.priorities[priority]
            sm = self.statuses[status]

            issue = {}
            if assigned:
                issue['assignee'] = self.users[assigned]
            else:
                issue['assignee'] = None
            issue['component'] = None
            issue['content'] = ''
            issue['content_updated_on'] = convert_date_format(creation)
            issue['created_on'] = convert_date_format(creation)
            issue['edited_on'] = None
            issue['id'] = pk
            issue['kind'] = p2p[pm][0]
            issue['milestone'] = 'M1'
            issue['priority'] = p2p[pm][1]
            issue['reporter'] = self.users[creator]
            issue['status'] = s2s[sm]
            issue['title'] = title
            issue['updated_on'] = convert_date_format(activity)
            issue['version'] = None
            issue['watchers'] = None
            issue['voters'] = None

            self.data['issues'].append(issue)

    def convert_messages(self):
        """
        Convert the messages related to Roundup issues to the comment format expected by Bitbuckets issue tracker.
        :return:
        """
        query = "SELECT * FROM _msg AS m, issue_messages AS im WHERE m.id=im.linkid"
        self.nr_comments = 0
        for row in self.c.execute(query):
            self.nr_comments += 1
            activity, actor, author, content, creation, creator, date, inreplyto, messageid, summary, type_, pk, retired, link_id, node_id = row

            mot = int(pk / 1000)
            msg_file_path = os.path.join(self.input_path, 'db', 'files', 'msg', '%d' % mot, 'msg%d' % pk)
            if os.path.exists(msg_file_path):
                msg_file = open(msg_file_path)
                real_content = msg_file.read()
                msg_file.close()
            else:
                logging.warning('Could not find msg %s file using summary', msg_file_path)
                real_content = summary

            NR_COMPARE_CHARS = 3
            if real_content[:NR_COMPARE_CHARS] != summary[:NR_COMPARE_CHARS]:
                raise RuntimeError(
                    'error opening %s %s %s' % (msg_file_path, real_content[:NR_COMPARE_CHARS], summary[:NR_COMPARE_CHARS]))
            message = {
                'content': real_content,
                'created_on': convert_date_format(creation),
                'id': pk,
                'issue': node_id,
                'updated_on': convert_date_format(activity),
                'user': self.users[creator],
            }

            self.data['comments'].append(message)

    def convert_attachments(self):
        """
        Convert the attachments from the SQlite Roundup database to the JSON structure Bitbucket expects and add all
        attachments to the ZIP file.
        :return:
        """
        query = "SELECT * FROM _file AS f, issue_files AS if WHERE f.id=if.linkid"
        self.nr_attachments = 0
        for row in self.c.execute(query):
            self.nr_attachments += 1
            activity, actor, content, creation, creator, name, type_, pk, retired, link_id, node_id = row
            mot = int(pk / 1000)
            att_file_path = os.path.join(self.input_path, 'db', 'files', 'file', '%d' % mot, 'file%d' % pk)
            arc_name = os.path.join('attachments', 'file%d' % pk)
            self.bb_zipfile.write(att_file_path, arc_name)

            attachment = {
                'filename': name,
                'issue': node_id,
                'path': arc_name,
                'user': self.users[creator],
            }

            self.data['attachments'].append(attachment)

    def read(self, input_path):
        self.input_path = input_path

        backend_path = os.path.join(self.input_path, 'db', 'backend_name')
        if not os.path.exists(backend_path):
            raise RuntimeError("The Roundup backend name file could not be found.")

        backend_name = open(backend_path, 'r').read()
        if backend_name.strip() != 'sqlite':
            raise RuntimeError('Only SQLite3 backends are supported.')

        sqlite_file = os.path.join(self.input_path, 'db', 'db')
        if not os.path.exists(sqlite_file):
            raise RuntimeError("The Roundup SQLite3 database could not be found.")

        conn = sqlite3.connect(sqlite_file)
        self.c = conn.cursor()

        for username, pk in self.c.execute("SELECT _username, id FROM _USER"):
            self.users[pk] = username

        for name, pk in self.c.execute("SELECT _name, id FROM _STATUS"):
            self.statuses[pk] = name

        for name, pk in self.c.execute("SELECT _name, id FROM _PRIORITY"):
            self.priorities[pk] = name

    def convert(self, output_file):
        if os.path.exists(output_file):
            raise RuntimeError("The file specified for output, already exists.")

        # XXX: Not using LZMA as BitBuckets importer does not seem to support it
        self.bb_zipfile = zipfile.ZipFile(output_file, mode='w')

        self.convert_issues()
        self.convert_messages()
        self.convert_attachments()
        self.bb_zipfile.writestr('db-1.0.json', json.dumps(self.data, indent=4))

    def close(self):
        self.bb_zipfile.close()
        self.c.close()

    def report(self):
        print("Converted %d issues, containing %d comments and %d attachments." % (self.nr_issues, self.nr_comments, self.nr_attachments))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('output_file')
    args = parser.parse_args()

    r = RoundupReader()
    r.read(args.path)
    r.convert(args.output_file)
    r.close()
    r.report()
