# -*- coding: utf-8 -*-

import sys

from django.conf import settings as project_settings

ENTITY_LOGO_DIR = getattr(project_settings, 'ENTITY_LOGO_DIR', 'entities/logos')
CONTACT_PHOTO_DIR = getattr(project_settings, 'CONTACT_PHOTO_DIR', 'contacts/photos')
CONTACTS_IMPORT_DIR = getattr(project_settings, 'CSV_IMPORT_DIR', 'imports')
OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT = getattr(project_settings, 'OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT', True)
ZONE_GROUP_SEARCH = getattr(project_settings, 'SANZA_ZONE_GROUP_SEARCH', False)


def get_default_country():
    return getattr(project_settings, 'SANZA_DEFAULT_COUNTRY', 'France')

ALLOW_COUPLE_GENDER = getattr(project_settings, 'SANZA_ALLOW_COUPLE_GENDER', False)
ALLOW_SINGLE_CONTACT = getattr(project_settings, 'SANZA_ALLOW_SINGLE_CONTACT', True)
NO_ENTITY_TYPE = getattr(project_settings, 'SANZA_NO_ENTITY_TYPE', False)


def is_unaccent_filter_supported():
    if 'test' in sys.argv:
        return False
    return getattr(project_settings, 'SANZA_UNACCENT_FILTER_SUPPORT', False)


def city_formatters():
    return getattr(project_settings, 'SANZA_CITY_FORMATTERS', ())