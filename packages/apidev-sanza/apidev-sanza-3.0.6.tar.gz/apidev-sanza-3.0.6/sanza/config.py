# -*- coding: utf-8 -*-
"""configure the sanza search form"""

from django.utils.translation import ugettext as _

from sanza.Crm import settings
from sanza.Crm import search_forms
from sanza.Emailing import search_forms as emailing_search_forms

SEARCH_FORMS = [
    (
        _(u'Group'),
        [
            search_forms.GroupSearchForm,
            search_forms.GroupSearchFormDropdownWidget,
            search_forms.NotInGroupSearchForm,
            search_forms.GroupsMemberOfAllSearchForm,
            search_forms.GroupsMemberOfAnySearchForm,
            search_forms.GroupsMemberOfNoneSearchForm,
        ],
    ), (
        _(u'Location'),
        [
            search_forms.CitySearchForm,
            search_forms.EntityCitySearchForm,
            search_forms.DepartmentSearchForm,
            search_forms.EntityDepartmentSearchForm,
            search_forms.RegionSearchForm,
            search_forms.EntityRegionSearchForm,
            search_forms.CountrySearchForm,
            search_forms.EntityCountrySearchForm,
            search_forms.ZipCodeSearchForm,
            search_forms.EntityZipCodeSearchForm,
            search_forms.HasCityAndZipcodeForm,
            search_forms.ZoneGroupSearchForm if (settings.ZONE_GROUP_SEARCH) else None,
            search_forms.EntityZoneGroupSearchForm if (settings.ZONE_GROUP_SEARCH) else None,
        ],
    ), (
        _(u'Entity'),
        [
            search_forms.EntityNameSearchForm,
            search_forms.EntityNameStartsWithSearchForm,
            search_forms.TypeSearchForm if (not settings.NO_ENTITY_TYPE) else None,
            search_forms.HasEntityForm if (settings.ALLOW_SINGLE_CONTACT) else None,
            search_forms.RelationshipDateForm,
            search_forms.EntityByModifiedDate,
            search_forms.EntityWithCustomField,
            search_forms.EntityDescriptionForm,
            search_forms.EntityNotesForm,
        ],
    ), (
        _(u'Contacts'),
        [
            search_forms.ContactNameSearchForm,
            search_forms.ContactFirstnameSearchForm,
            search_forms.ContactRoleSearchForm,
            search_forms.ContactByModifiedDate,
            search_forms.ContactAcceptSubscriptionSearchForm,
            search_forms.ContactRefuseSubscriptionSearchForm,
            search_forms.SecondarySearchForm,
            search_forms.ContactAgeSearchForm,
            search_forms.ContactsRelationshipByType,
            search_forms.ContactsRelationshipByDate,
            search_forms.ContactWithCustomField,
            search_forms.ContactNotesSearchForm,
            search_forms.ContactHasLeft,
            search_forms.EmailSearchForm,
            search_forms.ContactLanguageSearchForm,
        ],
    ), (
        _(u'Actions'),
        [
            search_forms.ActionNameSearchForm,
            search_forms.ActionTypeSearchForm,
            search_forms.ActionInProgressForm,
            search_forms.ActionByDoneDate,
            search_forms.ActionByPlannedDate,
            search_forms.ActionByStartDate,
            search_forms.ActionByUser,
            search_forms.ActionStatus,
            search_forms.ActionLtAmount,
            search_forms.ActionGteAmount,
            search_forms.HasAction,
        ],
    ), (
        _(u'Opportunities'),
        [
            search_forms.OpportunitySearchForm,
            search_forms.OpportunityNameSearchForm,
        ],
    ), (
        _(u'Emailing'),
        [
            emailing_search_forms.EmailingContactsSearchForm,
            emailing_search_forms.EmailingSentSearchForm,
            emailing_search_forms.EmailingOpenedSearchForm,
            emailing_search_forms.EmailingSendToSearchForm,
            emailing_search_forms.EmailingBounceSearchForm,
        ],
    ), (
        _(u'Admin'),
        [
            search_forms.ContactsImportSearchForm,
            search_forms.ContactHasEmail,
            search_forms.ContactHasPersonalEmail,
            search_forms.UnknownContact,
            search_forms.ContactsAndEntitiesByChangeDate,
            search_forms.ContactsByCreationDate,
            search_forms.ContactsByUpdateDate,
            search_forms.EntitiesByCreationDate,
            search_forms.EntitiesByUpdateDate,
        ],
    ), (
        _(u'Options'),
        [
            search_forms.NoSameAsForm,
            search_forms.SortContacts,
        ],
    ),
]
