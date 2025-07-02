import io
import json
import tempfile

from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_api_key.models import APIKey

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from api import get_user_preferences_attributes
from user_preferences.models import (
    UserPreferencesData,
    UserSettings,
    UserSettingsApp,
    UserSettingsValue,
)

from .views.user_settings import UserSettingsViewSet

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp()


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
        )
        self.url = reverse('user', kwargs={'version': 'v1'})

    def test_retrieve(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        content = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['uuid'], 'testuser')
        self.assertEqual(content['name'], 'Test User')
        self.assertEqual(content['email'], '')
        self.assertEqual(content['permissions'], [])
        self.assertEqual(
            content['profile'],
            [{'label': 'E-Mail', 'data': {'value': '', 'url': 'mailto:'}}],
        )
        self.assertEqual(content['space'], 10485760)
        self.assertIsNone(content['showroom_id'])


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class UserImageViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user_image', kwargs={'version': 'v1'})

    def test_list_no_preferences(self):
        # No UserPreferencesData row exists
        user = User.objects.create_user(username='user1')
        UserPreferencesData.objects.filter(user=user).delete()

        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_no_image(self):
        # Preferences exist but no image set
        user = User.objects.create_user(username='user2')
        UserPreferencesData.objects.filter(user=user).delete()
        UserPreferencesData.objects.create(user=user)

        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_list_and_delete_image(self):
        user = User.objects.create_user(username='user_single')
        UserPreferencesData.objects.filter(user=user).delete()
        UserPreferencesData.objects.create(user=user)

        self.client.force_authenticate(user=user)

        img_io = io.BytesIO()
        Image.new('RGB', (1, 1), color='white').save(img_io, format='PNG')
        img_io.seek(0)
        image = SimpleUploadedFile(
            name='avatar.png',
            content=img_io.read(),
            content_type='image/png',
        )

        post_response = self.client.post(
            self.url,
            {'user_image': image},
            format='multipart',
        )
        self.assertEqual(post_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(post_response.data, str)
        image_url = post_response.data

        list_response = self.client.get(self.url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, image_url)

        delete_response = self.client.delete(self.url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        final_response = self.client.get(self.url)
        self.assertEqual(final_response.status_code, status.HTTP_404_NOT_FOUND)


class UserPreferencesAgentViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='agentuser')
        self.api_key_obj, self.api_key = APIKey.objects.create_key(name='test')
        self.url = reverse(
            'users-detail',
            kwargs={'version': 'v1', 'pk': self.user.username},
        )

    def test_retrieve_with_valid_key(self):
        response = self.client.get(self.url, HTTP_X_API_KEY=self.api_key)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, get_user_preferences_attributes(self.user))

    def test_retrieve_no_user(self):
        self.client.credentials(HTTP_X_API_KEY=self.api_key)

        url = reverse('users-detail', kwargs={'version': 'v1', 'pk': 'nosuch'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User does not exist', response.json()['detail'])


class UserPreferencesDataViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user_data', kwargs={'version': 'v1'})

    def test_retrieve_exists(self):
        user = User.objects.create_user(username='datuser1')
        UserPreferencesData.objects.filter(user=user).delete()
        UserPreferencesData.objects.create(
            user=user,
            complementary_email='comp@example.com',
        )

        self.client.force_authenticate(user=user)
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('complementary_email'), 'comp@example.com')

    def test_retrieve_not_exists_returns_defaults(self):
        user = User.objects.create_user(username='datuser2')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # expertise is in serializer, defaults to None or []
        self.assertIn('expertise', response.data)

    def test_update_expertise_with_put(self):
        user = User.objects.create_user(username='updateprefs')
        UserPreferencesData.objects.filter(user=user).delete()
        UserPreferencesData.objects.create(user=user)

        self.client.force_authenticate(user=user)
        get_response = self.client.get(self.url, format='json')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        payload = {key: json.dumps(value) for key, value in get_response.data.items()}
        new_expertise = [
            {'label': {'en': 'Expert A'}},
            {'label': {'en': 'Expert B'}},
        ]
        payload['expertise'] = json.dumps(new_expertise)

        put_response = self.client.put(self.url, payload, format='multipart')
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.data.get('expertise'), new_expertise)


class UserSettingsViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='setuser')
        self.app = UserSettingsApp.objects.create(
            id='app1',
            name='Test App',
        )
        self.setting = UserSettings.objects.create(
            id='setting1',
            app=self.app,
            title={'en': 'Test Setting'},
            value_type='boolean',
            default_value=True,
        )
        self.url = reverse('user_settings', kwargs={'version': 'v1'})

    def test_retrieve_not_exists(self):
        User = get_user_model()  # noqa: N806
        fake_user = User(username='fakeasd_user')

        self.client.force_authenticate(user=fake_user)
        response = self.client.get(self.url, user=fake_user)

        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
        self.assertIn('settings', response.data[0])

    def test_retrieve_exists(self):
        self.client.force_authenticate(user=self.user)

        UserSettingsValue.objects.create(
            user=self.user,
            user_settings=self.setting,
            value=True,
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_valid_boolean_value(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            self.setting.id: True,
        }

        response = self.client.put(
            self.url,
            {'data': json.dumps(payload)},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        found = False
        for app_data in response.data:
            for setting_data in app_data.get('settings', []):
                if setting_data['id'] == self.setting.id:
                    self.assertEqual(setting_data['value'], True)
                    found = True
        self.assertTrue(found, 'Updated setting not found in response data')
        self.assertTrue(
            UserSettingsValue.objects.filter(
                user=self.user,
                user_settings=self.setting,
                value=True,
            ).exists(),
        )

    def test_destringify_value_boolean_true(self):
        view = UserSettingsViewSet()

        result = view.destringify_value('True', 'boolean')
        self.assertTrue(result)

        result_lower = view.destringify_value('false', 'boolean')
        self.assertFalse(result_lower)

    def test_validate_value_list_of_strings(self):
        view = UserSettingsViewSet()

        valid_list = ['one', 'two', 'three']
        self.assertTrue(view.validate_value(valid_list, 'list'))

        invalid_list = ['one', 2, 'three']
        self.assertFalse(view.validate_value(invalid_list, 'list'))

        empty_list = []
        self.assertFalse(view.validate_value(empty_list, 'list'))


class AutoSuggestLookupViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='abcuser')
        self.client.force_authenticate(user=self.user)

        self.url = reverse(
            'lookup_all',
            kwargs={'version': 'v1', 'fieldname': 'expertise'},
        )

    def test_lookup_view(self):
        source = settings.ACTIVE_SOURCES.get('expertise')
        self.assertIsInstance(source, dict)

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()

        self.assertIsInstance(content, list)
        for element in content:
            self.assertIsInstance(element, dict)


class AutoSuggestLookupSearchTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='abcuser')
        self.client.force_authenticate(user=self.user)

        self.url = reverse(
            'lookup',
            kwargs={'version': 'v1', 'fieldname': 'expertise', 'searchstr': 'test'},
        )

    def test_lookup_view_search(self):
        source = settings.ACTIVE_SOURCES.get('expertise')
        self.assertIsInstance(source, dict)

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()

        self.assertIsInstance(content, list)
        for element in content:
            self.assertIsInstance(element, dict)


class AutoSuggestUserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username='john', first_name='John', last_name='Doe')
        User.objects.create_user(username='jane', first_name='Jane', last_name='Smith')
        self.auth_user = User.objects.create_user(username='authuser')
        self.client.force_authenticate(user=self.auth_user)
        self.url = reverse(
            'autosuggest_user',
            kwargs={'version': 'v1', 'user': 'example'},
        )

    def test_autosuggest_user_no_match(self):
        # Searching for something that matches no first_name or last_name
        url = reverse(
            'autosuggest_user',
            kwargs={'version': 'v1', 'user': 'xyz'},
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 0)

    def test_autosuggest_user_match_first_name(self):
        # Partial first_name "Jan" should match "Jane Smith"
        url = reverse(
            'autosuggest_user',
            kwargs={'version': 'v1', 'user': 'Jan'},
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()
        self.assertEqual(len(content), 1)

        result = content[0]

        self.assertIsInstance(result, dict)
        self.assertEqual(result['UUID'], 'jane')
        self.assertEqual(result['first_name'], 'Jane')
        self.assertEqual(result['last_name'], 'Smith')
        self.assertEqual(result['label'], 'Jane Smith')

    def test_autosuggest_user_match_last_name(self):
        # Partial last_name "Do" should match "John Doe"
        url = reverse(
            'autosuggest_user',
            kwargs={'version': 'v1', 'user': 'Do'},
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.json()
        self.assertEqual(len(content), 1)

        result = content[0]

        self.assertIsInstance(result, dict)
        self.assertEqual(result['UUID'], 'john')
        self.assertEqual(result['first_name'], 'John')
        self.assertEqual(result['last_name'], 'Doe')
        self.assertEqual(result['label'], 'John Doe')
