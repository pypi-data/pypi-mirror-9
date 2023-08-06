# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('form_name', models.CharField(help_text='Used to distinguish multiple contact forms on the same site.', max_length=60, verbose_name='Form name', blank=True)),
                ('form_layout', models.CharField(help_text='Choice the layout of contact form', max_length=255, verbose_name='Form Layout', choices=[(b'cmsplugin_contact.forms.ContactForm', b'Default')])),
                ('site_email', models.EmailField(max_length=75, verbose_name='Email recipient')),
                ('thanks', models.TextField(default='Thank you for your message.', help_text='Message displayed on successful submit', max_length=200, verbose_name='Thanks message')),
                ('submit', models.CharField(default='Submit', max_length=30, verbose_name='Submit button value')),
                ('spam_protection_method', models.SmallIntegerField(default=0, verbose_name='Spam protection method', choices=[(0, b'Honeypot'), (1, b'Akismet'), (2, b'ReCAPTCHA')])),
                ('akismet_api_key', models.CharField(max_length=255, blank=True)),
                ('recaptcha_public_key', models.CharField(max_length=255, blank=True)),
                ('recaptcha_private_key', models.CharField(max_length=255, blank=True)),
                ('recaptcha_theme', models.CharField(default=b'clean', max_length=20, verbose_name='ReCAPTCHA theme', choices=[(b'clean', b'Clean'), (b'red', b'Red'), (b'white', b'White'), (b'blackglass', b'Black Glass'), (b'custom', b'Custom')])),
                ('redirect_url', models.URLField(help_text='If it is set, the form redirect to url when the form is valid', verbose_name='URL Redirection', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
