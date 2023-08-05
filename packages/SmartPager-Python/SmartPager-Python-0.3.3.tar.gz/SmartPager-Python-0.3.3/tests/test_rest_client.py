
import unittest
import logging
import sys

from smartpager.rest.base import RESTClient
from smartpager.resources.models import SmartPagerMessageType


log = logging.getLogger(__name__)


class TestRestClient(unittest.TestCase):

    # Test API user token
    auth_token = '51e1cb4be06bd72c1f55441365cb7bf47aecbf8a'
    base_url = 'http://localhost:8000/api/v1/'

    def setUp(self):
        self.auth = 'Token {}'.format(self.auth_token)
        self.client = RESTClient(self.base_url, self.auth)

    def test_get_user(self):
        """
        :assumption: There exists a user with ID=1 to be returned
        """
        resource = self.client.users.get(1)
        self.assertIsNotNone(resource, 'users.get should return a user')

    def test_list_users(self):
        """
        :assumption: There exists a user with ID=1 to be returned
        """
        params = {
            'id': 1,
        }

        single_user = self.client.users.list(params)
        self.assertIsNotNone(single_user, msg='users.list() should return a list of users.')

        users = self.client.users.list({})
        self.assertIsNotNone(users, msg='users.list() should return users.')
        self.assertGreaterEqual(len(users), len(single_user), msg='users.list({}) should retrieve all users.')

    def test_get_broadcast_paginggroups(self):

        group = self.client.paginggroups.get(1)
        self.assertIsNotNone(group, 'paginggroups.get should return a group')

    def test_list_broadcast_paginggroups(self):

        params = {
            'id': 1,
        }

        single_p_group = self.client.paginggroups.list(params)

        self.assertIsNotNone(single_p_group, 'paginggroups.list({id:1}) should return a group')

        p_groups = self.client.paginggroups.list({})
        self.assertIsNotNone(p_groups, 'groups.list({}) should retrieve a list of all groups.')
        self.assertGreaterEqual(len(p_groups), len(single_p_group), msg='groups.list({}) should retrieve all groups.')

    def test_get_schedule_paginggroups(self):

        group = self.client.paginggroups.get(2)
        self.assertIsNotNone(group, 'paginggroups.get should return a group')

    def test_list_schedule_paginggroups(self):

        params = {
            'id': 2,
        }

        single_p_group = self.client.paginggroups.list(params)

        self.assertIsNotNone(single_p_group, 'paginggroups.list({id:1}) should return a group')

        p_groups = self.client.paginggroups.list({})
        self.assertIsNotNone(p_groups, 'groups.list({}) should retrieve a list of all groups.')
        self.assertGreaterEqual(len(p_groups), len(single_p_group), msg='groups.list({}) should retrieve all groups.')

    def test_list_schedule_occurrences(self):
        params = {
            # 'id': 2,
            'start': 1404325354,
            'end': 1404325355,
        }

        occurrences = self.client.paginggroups.get(2, params)

        occurrences = [occurrences]

        print 'Schedule Group Occurrences: {}'.format(occurrences)
        for group in occurrences:

            print '-------------------------------------------------'
            print 'Name: {}'.format(group.name)
            print 'Users: {}'.format(group.users)
            print 'Occurrences: {}'.format(group.occurrences)
            print '-------------------------------------------------'

        self.assertIsNotNone(occurrences, 'paginggroups list start to end should return occurrences')
        self.assertGreaterEqual(len(occurrences), 1, 'paginggroup list start to end should return at least 1 event')

    def test_get_account(self):
        """
        :assumption: There exists an account with ID=1 to be returned
        """
        account = self.client.accounts.get(91)
        self.assertIsNotNone(account, 'accounts.get should return an account.')

    def test_list_accounts(self):
        """
        :assumption: There exists an account with ID=1 to be returned
        """
        params = {
            'id': 1,
        }

        single_account = self.client.accounts.list(params)
        self.assertIsNotNone(single_account, 'accounts.list() should return an account')

        accounts = self.client.accounts.list({})
        self.assertIsNotNone(accounts, 'accounts.list({}) should retrieve a list of all accounts')

        self.assertGreaterEqual(len(accounts), len(single_account),
                                msg='accounts.list({}) should retrieve a list of all accounts')

    def test_get_messagetype(self):
        """
        :assumption: There exists a message type with ID=1 to be returned
        """
        messagetype = self.client.messagetypes.get(1)
        self.assertIsNotNone(messagetype, 'messagetypes.get() should return a message type.')

    def test_list_messagetypes(self):
        """
        :assumption: There exists a message type with ID=1 to be returned
        """
        params = {
            'telephone_friendly': 'true',
            'id': 1,
        }
        single_mt = self.client.messagetypes.list(params)
        self.assertIsNotNone(single_mt, 'messagetypes.list() should return a message type.')

        self.assertIsInstance(single_mt, type([]), 'list should return a list')
        self.assertGreaterEqual(len(single_mt), 1, 'Message type (list) should have retrieved at least one messagetype')

        # self.assertEqual(type(single_mt), SmartPagerMessageType, 'Single MT should be MT. Is {}'.format(single_mt))

        mts = self.client.messagetypes.list({})

        self.assertIsNotNone(mts, 'messagetypes.list({}) should return a message type.')
        self.assertGreaterEqual(len(mts), len(single_mt), 'messagetypes.list({}) should return a list of messagetypes.')

        for mt in mts:
            print 'Message Type Fields: ' + str(['field: ' + str(field) for field in mt.fields])

    def test_list_oncalls(self):
        """
        Special resource!

        Requires the paging group id to work. Gets all the users who are oncall for a specific paging group
        :return:
        """

        params = {
            'id': 2,
            'url_extension': 'oncall',
        }

        oncalls = self.client.oncalls.list(params)

        self.assertIsNotNone(oncalls)


if __name__ == '__name__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(__name__).setLevel(logging.info)
    unittest.main()