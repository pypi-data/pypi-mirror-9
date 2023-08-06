# -*- coding: utf8 -*-

import unittest2 as unittest

from ecreall.helpers.testing.base import BaseTest

from collective.dms.basecontent.testing import DMS_TESTS_PROFILE_FUNCTIONAL
from ..source import RecipientGroupsVocabulary, TreatingGroupsVocabulary


class TestDmsdocument(unittest.TestCase, BaseTest):
    """Tests adapters"""

    layer = DMS_TESTS_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestDmsdocument, self).setUp()
        self.portal = self.layer['portal']

    def test_RecipientGroupsVocabulary(self):
        voc_inst = RecipientGroupsVocabulary()
        voc_ids = [i.token for i in voc_inst(self.portal).__iter__()]
        self.assertEqual(set(voc_ids), set(['Administrators',
                                             'Reviewers', 'Site Administrators']))
        voc_ids = [i.token for i in voc_inst(self.portal).search('user')]
        self.assertEqual(set(voc_ids), set(['test_user_1_', 'AuthenticatedUsers']))

    def test_TreatingGroupsVocabulary(self):
        voc_inst = TreatingGroupsVocabulary()
        voc_ids = [i.token for i in voc_inst(self.portal).__iter__()]
        self.assertEqual(set(voc_ids), set(['Administrators',
                                             'Reviewers', 'Site Administrators']))
        voc_ids = [i.token for i in voc_inst(self.portal).search('user')]
        self.assertEqual(set(voc_ids), set(['test_user_1_', 'AuthenticatedUsers']))
