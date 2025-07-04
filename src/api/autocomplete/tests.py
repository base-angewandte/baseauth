from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse


class AutoCompleteViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('autocomplete', kwargs={'version': 'v2'})
        self.User = get_user_model()

        self.auth_user = self.User.objects.create_user(
            username='tester',
            email='tester@example.com',
        )
        self.client.force_authenticate(user=self.auth_user)

        self.source_name = next(iter(settings.ACTIVE_SOURCES.keys()))
        if self.source_name == 'users' and len(settings.ACTIVE_SOURCES) > 1:
            self.source_name = list(settings.ACTIVE_SOURCES.keys())[1]

    def test_users_search_respects_limit(self):
        self.User.objects.create_user(
            username='anna',
            first_name='Anna',
            last_name='Muster',
        )
        self.User.objects.create_user(
            username='anne',
            first_name='Anne',
            last_name='Example',
        )
        self.User.objects.create_user(
            username='bob',
            first_name='Bob',
            last_name='Builder',
        )

        response = self.client.get(self.url, {'type': 'users', 'q': 'ann', 'limit': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()
        self.assertEqual(len(content), 1)
        self.assertSetEqual(
            set(content[0]),
            {'UUID', 'first_name', 'last_name', 'label'},
        )

    def test_lookup_with_query(self):
        response = self.client.get(
            self.url,
            {'type': self.source_name, 'q': 'test'},
            HTTP_ACCEPT_LANGUAGE='en',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)

    def test_lookup_all_items(self):
        response = self.client.get(
            self.url,
            {'type': self.source_name},
            HTTP_ACCEPT_LANGUAGE='en',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)

    def test_limit(self):
        response = self.client.get(
            self.url,
            {'type': 'users', 'q': 'ann', 'limit': 0},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['detail'], 'limit must be a positive integer')

    def test_missing_type_parameter(self):
        resp = self.client.get(self.url, {'q': 'ann'})

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['error'], 'Missing required "type" parameter.')
