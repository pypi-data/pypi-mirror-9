# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.core.urlresolvers import reverse
from django.test import TestCase

from ralph.ui.tests.global_utils import login_as_su
from ralph_assets.tests.utils import MessagesTestMixin, UserFactory
from ralph_assets.tests.utils.licences import LicenceFactory


class TestUserListView(MessagesTestMixin, TestCase):

    def setUp(self):
        self.client = login_as_su()

    def test_users_view(self):
        user = UserFactory(**{'username': 'test_user'})
        user_page_url = reverse('user_view', args=(user.username,))
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.username in response.content)
        self.assertTrue(user_page_url in response.content)


class TestUserDetailView(MessagesTestMixin, TestCase):
    def setUp(self):
        self.client = login_as_su()

    def test_users_view_not_found(self):
        invalid_url = reverse('user_view', args=('invalid_username',))
        response = self.client.get(invalid_url, follow=True)
        self.assertMessageEqual(
            response,
            'User {} not found'.format('invalid_username'),
        )


class TestUserEditRelations(TestCase):

    def setUp(self):
        self.client = login_as_su()

    def test_users_view(self):
        user = UserFactory(**{'username': 'test_user'})
        url = reverse('edit_user_relations', args=(user.username,))
        self.assertEqual(user.licences.count(), 0)
        post_data = {
            'licences': '|'.join([
                str(LicenceFactory().id) for i in range(5)]
            )
        }
        self.client.post(url, post_data, follow=True)
        self.assertEqual(user.licences.count(), 5)
