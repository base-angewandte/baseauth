import itertools
import logging
import os

import shortuuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _

logger = logging.getLogger(__name__)


def user_directory_path(instance, filename):
    path, ext = os.path.splitext(filename)

    s_uuid = shortuuid.uuid()
    return f'{s_uuid}{ext}'


class UserPreferencesData(models.Model):
    user = models.OneToOneField(
        get_user_model(), primary_key=True, on_delete=models.CASCADE
    )
    showroom_id = models.CharField(max_length=255, blank=True, null=True)

    # Editable
    complementary_email = models.EmailField(
        verbose_name=_('E-Mail (complementary)'), blank=True, null=True
    )
    # urls = JSONField(verbose_name=_('URLs'), blank=True, null=True)

    urls = models.URLField(
        verbose_name=_('Website'), max_length=255, blank=True, null=True
    )

    expertise = JSONField(verbose_name=_('Skills and Expertise'), blank=True, null=True)
    orcid_pid = models.CharField(max_length=255, blank=True, null=True)
    gnd_viaf = models.CharField(
        max_length=255, blank=True, null=True
    )  # todo should be array or anyway multiple should be available

    # still missing and TODO
    # Recherche / basis wien = somefield

    user_image = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
    )

    # Non_editable_data
    affiliation = JSONField(blank=True, null=True)
    organisational_unit = JSONField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)

    # Location fields
    street_address = JSONField(blank=True, null=True)
    postal_code = JSONField(blank=True, null=True)
    office = JSONField(blank=True, null=True)
    place = JSONField(blank=True, null=True)
    country_or_region = JSONField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_changed = models.DateTimeField(auto_now=True, editable=False)

    @property
    def location_object(self):
        if self.street_address:
            return {
                'street_address': self.street_address[0]
                if self.street_address
                else None,
                'postal_code': self.postal_code[0] if self.postal_code else None,
                'office': self.office[0] if self.office else None,
                'place': self.place[0] if self.place else None,
                'country_or_region': self.country_or_region[0]
                if self.country_or_region
                else None,
            }

    @property
    def location(self):
        location_attrs = [
            self.street_address,
            self.postal_code,
            self.office,
            self.organisational_unit,  # department
            self.affiliation,  # company
            self.place,
            self.country_or_region,
        ]

        zipped = list(
            itertools.zip_longest(
                *[location_item for location_item in location_attrs if location_item]
            )
        )

        return ', '.join(
            [
                ', '.join(list(i))
                for i in [
                    list(filter(None, location_element)) for location_element in zipped
                ]
            ]
        )

    @property
    def profile(self):
        ret = []

        if self.affiliation:
            ret.append(
                {
                    'label': _('Affiliation'),
                    'data': self.affiliation[0],
                }
            )

        if self.organisational_unit:
            ret.append(
                {
                    'label': _('Organisational Unit'),
                    'data': self.organisational_unit[0],
                }
            )

        # TODO position

        ret.append(
            {
                'label': _('E-Mail'),
                'data': {'value': self.user.email, 'url': f'mailto:{self.user.email}'},
            }
        )

        if self.telephone:
            ret.append(
                {
                    'label': _('Telephone'),
                    'data': self.telephone[0],
                }
            )

        # if self.fax:
        #     ret.append({
        #         'label': _('FAX'),
        #         'data': self.fax[0],
        #     })

        if self.street_address:
            ret.append(
                {
                    'label': _('Address'),
                    'data': [
                        f'{self.street_address[0]}',
                        f'{self.postal_code[0]} {self.place[0]}'.strip(),
                    ],
                }
            )

        return ret

    @property
    def attrs_dict(self):
        # TODO add additional information
        attrs = {
            'skills': self.expertise,
            'complementary_email': self.complementary_email,
            'urls': self.urls,
            'organisational_unit': None,
            'telephone': None,
            'location': self.location_object,
            'image': None,
            'showroom_id': self.showroom_id,
        }
        if self.organisational_unit:
            attrs['organisational_unit'] = self.organisational_unit[0]
        if self.telephone:
            attrs['telephone'] = self.telephone[0]
        if self.user_image:
            image_url = reverse('user_image', kwargs={'image': self.user_image})
            attrs['image'] = f'{settings.SITE_URL.rstrip("/")}{image_url}'

        return attrs


class UserSettingsApp(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    icon = models.URLField(max_length=255, blank=True, null=True, default=None)


class UserSettings(models.Model):
    VALUE_TYPE = (
        ('boolean', _('Boolean')),
        ('string', _('String')),
        ('list', _('List of strings')),
    )

    id = models.CharField(max_length=255, primary_key=True)
    app = models.ForeignKey(UserSettingsApp, on_delete=models.CASCADE)
    title = JSONField(blank=True, null=True)
    value_type = models.CharField(max_length=255, choices=VALUE_TYPE, default='boolean')
    default_value = JSONField(blank=True, null=True)

    @property
    def value_schema(self):
        language = get_language() or 'en'
        ret = {
            'id': self.id,
            'title': self.title.get(language, '')
            if isinstance(self.title, dict)
            else self.title,
            'type': self.value_type,
            'value': self.default_value,
        }

        if self.value_type == 'boolean':
            ret.update({'x-attrs': {'field_type': 'boolean'}})

        return ret


class UserSettingsValue(models.Model):
    value = JSONField(blank=True, null=True)
    user_settings = models.ForeignKey(UserSettings, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @property
    def value_schema(self):
        schema = self.user_settings.value_schema

        schema['value'] = self.value

        # TODO find a better solution than hard coding
        if schema['id'] == 'activate_profile' and self.value:
            showroom_id = self.user.userpreferencesdata.showroom_id
            if showroom_id:
                schema['x-attrs']['subtext'] = {
                    'url': f'{settings.SHOWROOM_BASE_URL}{showroom_id}',
                    'value': f'{showroom_id}',
                }

        return schema


def settings_dict(user):
    ret = []

    for app in UserSettingsApp.objects.all():
        app_dict = {'app': app.id, 'icon': app.icon, 'title': app.name, 'settings': []}
        for setting in UserSettings.objects.filter(app=app):
            try:
                schema = UserSettingsValue.objects.get(
                    user_settings=setting, user=user
                ).value_schema
            except UserSettingsValue.DoesNotExist:
                schema = setting.value_schema
            app_dict['settings'].append(schema)
        ret.append(app_dict)

    return ret


def settings_dict_flat(user):
    ret = {}
    for app in UserSettingsApp.objects.all():
        s_dict = {}
        for setting in UserSettings.objects.filter(app=app):
            try:
                value = UserSettingsValue.objects.get(
                    user_settings=setting, user=user
                ).value
            except UserSettingsValue.DoesNotExist:
                value = setting.default_value
            s_dict[setting.id] = value
        ret[app.id] = s_dict
    return {'settings': ret} if ret else ret
