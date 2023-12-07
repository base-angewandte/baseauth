# Generated by Django 4.2.7 on 2023-12-07 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user_preferences.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreferencesData',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('showroom_id', models.CharField(blank=True, max_length=255, null=True)),
                ('complementary_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-Mail (complementary)')),
                ('urls', models.URLField(blank=True, max_length=255, null=True, verbose_name='Website')),
                ('expertise', models.JSONField(blank=True, null=True, verbose_name='Skills and Expertise')),
                ('orcid_pid', models.CharField(blank=True, max_length=255, null=True)),
                ('gnd_viaf', models.CharField(blank=True, max_length=255, null=True)),
                ('user_image', models.ImageField(blank=True, null=True, upload_to=user_preferences.models.user_directory_path)),
                ('affiliation', models.JSONField(blank=True, null=True)),
                ('organisational_unit', models.JSONField(blank=True, null=True)),
                ('position', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('telephone', models.CharField(blank=True, max_length=255, null=True)),
                ('fax', models.CharField(blank=True, max_length=255, null=True)),
                ('street_address', models.JSONField(blank=True, null=True)),
                ('postal_code', models.JSONField(blank=True, null=True)),
                ('office', models.JSONField(blank=True, null=True)),
                ('place', models.JSONField(blank=True, null=True)),
                ('country_or_region', models.JSONField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('title', models.JSONField(blank=True, null=True)),
                ('value_type', models.CharField(choices=[('boolean', 'Boolean'), ('string', 'String'), ('list', 'List of strings')], default='boolean', max_length=255)),
                ('default_value', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSettingsApp',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('icon', models.URLField(blank=True, default=None, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSettingsValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_preferences.usersettings')),
            ],
        ),
        migrations.AddField(
            model_name='usersettings',
            name='app',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_preferences.usersettingsapp'),
        ),
    ]