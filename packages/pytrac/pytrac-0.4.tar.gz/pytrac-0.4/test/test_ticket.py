import os
import sys
import xmlrpclib

pytrac_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.insert(0, pytrac_root)

import pytest
from mock import Mock
import datetime

from pytrac import Ticket


class TestTicket(object):

    def setup_class(self):
        server = Mock()
        self.ticket = Ticket(server)

    def testSearchWithAllParams(self):
        self.ticket.search(summary='test_summary', owner='someowner', status='new', ticket_type='Task', order='id', descending=True, max=10)
        self.ticket.api.query.assert_called_with('summary~=test_summary&owner=someowner&status=new&type=Task&order=id&desc=true&max=10')


class TestUpdateTicket(object):

    ticket_id = 1

    def setup_class(self):
        server = Mock()

        self.timestamp = datetime.datetime.now()

        self.ticket_ok_return_value = [
            self.ticket_id,
            self.timestamp,
            self.timestamp,
            {
                '_ts': self.timestamp,
                'action': 'leave',
            },
        ]

        server.ticket.get.return_value = self.ticket_ok_return_value
        server.ticket.update.return_value = self.ticket_ok_return_value

        server.ticket.getActions.return_value = [
            ['leave', 'leave', '.', []],
            ['resolve', 'resolve', "The resolution will be set. Next status will be 'closed'.",
                [['action_resolve_resolve_resolution', 'fixed',
                    ['fixed', 'worksforme']]]]]
        self.server = server
        self.ticket = Ticket(server)

    def testComment(self):
        self.ticket.comment(self.ticket_id, "some comment")
        self.ticket.api.update.assert_called_with(
            self.ticket_id,
            "some comment",
            {'action': 'leave', '_ts': self.timestamp},
            True)

    def testClose(self):
        self.ticket.close(self.ticket_id, "some comment")
        self.ticket.api.update.assert_called_with(
            self.ticket_id,
            "some comment",
            {'action': 'resolve',
             '_ts': self.timestamp,
             'action_resolve_resolve_resolution': 'fixed',
             'status': 'closed'},
            True)

    def testCommentWithRetries(self):

        self.server.ticket.update.side_effect = [
            xmlrpclib.Fault(1, 'bzzp bzzp error bzzp'),
            xmlrpclib.Fault(1, 'bzzp bzzp error bzzp'),
            self.ticket_ok_return_value,
        ]

        self.ticket.comment(self.ticket_id, "some comment")
        self.ticket.api.update.assert_called_with(
            self.ticket_id,
            "some comment",
            {'action': 'leave', '_ts': self.timestamp},
            True)

    def testCommentMaxRetriesReached(self):

        self.server.ticket.update.side_effect = [
            xmlrpclib.Fault(1, 'bzzp bzzp error bzzp'),
            xmlrpclib.Fault(1, 'bzzp bzzp error bzzp'),
            xmlrpclib.Fault(1, 'bzzp bzzp error bzzp')
        ]

        with pytest.raises(xmlrpclib.Fault):
            self.ticket.comment(self.ticket_id, "some comment")


if __name__ == '__main__':
    pytest.main(__file__)
