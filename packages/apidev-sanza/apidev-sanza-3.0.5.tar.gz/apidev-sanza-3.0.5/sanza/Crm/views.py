# -*- coding: utf-8 -*-

from datetime import date, datetime
import json
import os.path
import re

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages import api as user_message
from django.db.models import Q, Max
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.template.loader import find_template
from django.utils.translation import ugettext as _
from django.views.generic.dates import MonthArchiveView, WeekArchiveView, DayArchiveView
from django.views.generic import ListView

from colorbox.decorators import popup_redirect
from coop_cms.generic_views import EditableObjectView
from wkhtmltopdf.views import PDFTemplateView

from sanza.Crm import models, forms
from sanza.Crm import settings as crm_settings
from sanza.Crm.utils import get_actions_by_set
from sanza.Crm.settings import get_default_country, is_unaccent_filter_supported
from sanza.Crm.utils import unicode_csv_reader, resolve_city, check_city_exists, get_in_charge_users
from sanza.permissions import can_access
from sanza.utils import logger, log_error


@user_passes_test(can_access)
def view_entity(request, entity_id):
    
    entity = get_object_or_404(models.Entity, id=entity_id)
    contacts = entity.contact_set.all().order_by("has_left", "-main_contact", "lastname", "firstname")
    
    actions = models.Action.objects.filter(
        Q(entities=entity) | Q(contacts__entity=entity), Q(archived=False)
    ).distinct().order_by("planned_date", "priority")
    
    actions_by_set = get_actions_by_set(actions, 5)    
    
    multi_user = True
    request.session["redirect_url"] = reverse('crm_view_entity', args=[entity_id])
    
    context = {
        "entity": entity,
        'contacts': contacts,
        'actions_by_set': actions_by_set,
        'multi_user': multi_user,
    }
    
    return render_to_response(
        'Crm/entity.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_entities_list(request):
    letter_filter = request.GET.get("filter", "*")
    
    qs = models.Entity.objects.all()
    if re.search("\w+", letter_filter):
        if is_unaccent_filter_supported():
            qs = qs.extra(
                where=[u"UPPER(unaccent(name)) LIKE UPPER(unaccent(%s))"],
                params=[u"{0}%".format(letter_filter)]
            )
        else:
            qs = qs.filter(name__istartswith=letter_filter)
    elif letter_filter == "~":
        qs = qs.filter(name__regex=r'^\W|^\d')
    entities = list(qs)

    return render_to_response(
        'Crm/all_entities.html',
        {'entities': entities, "letter_filter": letter_filter},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_entity_to_group(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    if request.method == "POST":
        form = forms.AddEntityToGroupForm(entity, request.POST)
        if form.is_valid():
            name = form.cleaned_data["group_name"]
            
            group, is_new = models.Group.objects.get_or_create(name=name)
            group.entities.add(entity)
            group.save()
            next_url = reverse('crm_view_entity', args=[entity_id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.AddEntityToGroupForm(entity)
    
    context_dict = {
        'entity': entity,
        'form': form,
        'request': request,
    }

    return render_to_response(
        'Crm/add_entity_to_group.html',
        context_dict,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_contact_to_group(request, contact_id):
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)
        
        if request.method == "POST":
            form = forms.AddContactToGroupForm(contact, request.POST)
            if form.is_valid():
                name = form.cleaned_data["group_name"]
                group, is_new = models.Group.objects.get_or_create(name=name)
                if not (contact in group.contacts.all()):
                    group.contacts.add(contact)
                    group.save()
                next_url = reverse('crm_view_contact', args=[contact_id])
                return HttpResponseRedirect(next_url)
        else:
            form = forms.AddContactToGroupForm(contact)
        
        context_dict = {
            'contact': contact,
            'form': form,
        }
    
        return render_to_response(
            'Crm/add_contact_to_group.html',
            context_dict,
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        print "#ERR", msg
        raise


@user_passes_test(can_access)
@popup_redirect
def change_contact_entity(request, contact_id):
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)
        
        if request.method == "POST":
            form = forms.ChangeContactEntityForm(contact, request.POST)
            if form.is_valid():
                form.change_entity()
                next_url = reverse('crm_view_contact', args=[contact_id])
                return HttpResponseRedirect(next_url)
        else:
            form = forms.ChangeContactEntityForm(contact)
        
        context_dict = {
            'contact': contact,
            'form': form,
        }
    
        return render_to_response(
            'Crm/change_contact_entity.html',
            context_dict,
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        print "#ERR", msg
        raise


@user_passes_test(can_access)
def get_group_suggest_list(request):
    try:
        suggestions = []
        term = request.GET["term"]#the 1st chars entered in the autocomplete
        for group in models.Group.objects.filter(name__icontains=term):
            suggestions.append(group.name)
        return HttpResponse(json.dumps(suggestions), content_type='application/json')
    except Exception, msg:
        print '###', msg


@user_passes_test(can_access)
@popup_redirect
def remove_entity_from_group(request, group_id, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    group = get_object_or_404(models.Group, id=group_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                group.entities.remove(entity)
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity_id]))
    else:
        form = forms.ConfirmForm()
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to remove {0.name} from the {1.name} group?').format(entity, group),
            'action_url': reverse("crm_remove_entity_from_group", args=[group_id, entity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_contact_from_group(request, group_id, contact_id):
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)
        group = get_object_or_404(models.Group, id=group_id)
        if request.method == 'POST':
            form = forms.ConfirmForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["confirm"]:
                    group.contacts.remove(contact)
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact_id]))
        else:
            form = forms.ConfirmForm()
        return render_to_response(
            'sanza/confirmation_dialog.html',
            {
                'form': form,
                'message': _(u'Do you want to remove {0.fullname} from the {1.name} group?').format(contact, group),
                'action_url': reverse("crm_remove_contact_from_group", args=[group_id, contact_id]),
            },
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        print "#ERR", msg
        raise


@user_passes_test(can_access)
def edit_group(request, group_id):
    group = get_object_or_404(models.Group, id=group_id)
    next_url = request.session.get('next_url', reverse('crm_see_my_groups'))
    if request.method == "POST":
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            next_url = request.session.pop('next_url', reverse('crm_see_my_groups'))
            return HttpResponseRedirect(next_url)
    else:
        form = forms.EditGroupForm(instance=group)
    
    context_dict = {
        'form': form,
        'group': group,
        'request': request,
        'next_url': next_url,
    }

    return render_to_response(
        'Crm/edit_group.html',
        context_dict,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_group(request, group_id):
    group = get_object_or_404(models.Group, id=group_id)
    
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                group.delete()
                return HttpResponseRedirect(reverse("crm_see_my_groups"))
            else:
                return HttpResponseRedirect(reverse('crm_edit_group', args=[group.id]))
    else:
        form = forms.ConfirmForm()
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the group {0.name}?').format(group),
            'action_url': reverse("crm_delete_group", args=[group_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def add_group(request):
    
    if request.method == "POST":
        group = models.Group()
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm_see_my_groups'))
        group = None
    else:
        form = forms.EditGroupForm()
    
    return render_to_response(
        'Crm/edit_group.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def get_action_status(request):
    try:
        action_type_id = int(request.GET.get("t", 0))
    except ValueError:
        raise Http404
    
    default_status = 0
    if action_type_id:
        action_type = get_object_or_404(models.ActionType, id=action_type_id)
        allowed_status = [s.id for s in action_type.allowed_status.all()]
        if action_type.default_status:
            default_status = action_type.default_status.id   
    else:
        allowed_status = []
    return HttpResponse(json.dumps({'allowed_status': allowed_status, 'default_status': default_status}), content_type="application/json")


@user_passes_test(can_access)
def see_my_groups(request):
    
    ordering = request.GET.get('ordering', 'name')
    
    groups = models.Group.objects.all()
    
    if ordering == 'name':
        try:
            #may fail for some databases
            groups = groups.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except:
            groups = list(models.Group.objects.all())
            groups.sort(key=lambda g: g.name.lower()) #order groups with case-independant name
    else:
        groups = groups.order_by('-modified')
        
    return render_to_response(
        'Crm/my_groups.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def edit_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    #update last access
    entity.save()
    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity)

    return render_to_response(
        'Crm/edit_entity.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_entity(request, entity_type_id):
    try:
        entity_type_id = int(entity_type_id)
    except ValueError:
        raise Http404
    if entity_type_id:
        entity_type = get_object_or_404(models.EntityType, id=entity_type_id)
        entity = models.Entity(type=entity_type)
    else:
        entity = models.Entity()
    
    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity, initial={'relationship_date': date.today()})
        
    return render_to_response(
        'Crm/edit_entity.html',
        {
            'entity': entity,
            'form': form,
            'create_entity': True,
            'entity_type_id': entity_type_id,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                entity.delete()
                return HttpResponseRedirect(reverse('sanza_homepage'))
            else:
                return HttpResponseRedirect(reverse('crm_edit_entity', args=[entity.id]))
    else:
        form = forms.ConfirmForm()
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete {0.name}?').format(entity),
            'action_url': reverse("crm_delete_entity", args=[entity_id]),
        },
        context_instance=RequestContext(request)
    )


def get_city_name(request, city):
    #Anybody can accesss (public contact form of a website)
    try:
        city_id = int(city)
        city = models.City.objects.get(id=city_id)
        return HttpResponse(json.dumps({'name': city.name}), 'application/json')
    except ValueError:
        return HttpResponse(json.dumps({'name': city}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_city_id(request):
    name = (request.GET.get('name'))
    country_id = int(request.GET.get('country', 0))
    default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
    if country_id == 0 or country_id == default_country.id:
        cities = models.City.objects.filter(name__iexact=name).exclude(parent__code='')
    else:
        cities = models.City.objects.filter(name__iexact=name, parent__id=country_id)
    if cities.count() != 1:
        city_id = name
    else:
        city_id = cities[0].id
    return HttpResponse(json.dumps({'id': city_id}), 'application/json')


def get_cities(request):
    #subscribe form : no login required
    term = request.GET.get('term')
    country_id = int(request.GET.get('country', 0))
    default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
    if country_id == 0 or country_id == default_country.id:
        cities_queryset = models.City.objects.filter(name__icontains=term).exclude(parent__code='')[:10]
        cities = [{'id': x.id, 'name': x.name} for x in cities_queryset]
    else:
        cities_queryset = models.City.objects.filter(name__icontains=term, parent__id=country_id)[:10]
        cities = [{'id': x.id, 'name': x.name} for x in cities_queryset]
    return HttpResponse(json.dumps(cities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunity_name(request, opp_id):
    try:
        opp = models.Opportunity.objects.get(id=opp_id)
        return HttpResponse(json.dumps({'name': opp.name}), 'application/json')
    except (models.Opportunity.DoesNotExist, ValueError):
        return HttpResponse(json.dumps({'name': opp_id}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunities(request):
    term = request.GET.get('term')
    queryset = models.Opportunity.objects.filter(ended=False, name__icontains=term)
    opportunities = [{'id': x.id, 'name': u'{0}'.format(x.name)} for x in queryset]
    return HttpResponse(json.dumps(opportunities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunity_id(request):
    name = request.GET.get('name')
    opportunity = get_object_or_404(models.Opportunity, name=name)
    return HttpResponse(json.dumps({'id': opportunity.id}), 'application/json')


@user_passes_test(can_access)
def get_entity_name(request, entity_id):
    try:
        entity = models.Entity.objects.get(id=entity_id)
        return HttpResponse(json.dumps({'name': entity.name}), 'application/json')
    except models.Entity.DoesNotExist:
        return HttpResponse(json.dumps({'name': entity_id}), 'application/json')


@user_passes_test(can_access)
def get_entities(request):
    term = request.GET.get('term')
    entities = [{'id': x.id, 'name': x.name}
        for x in models.Entity.objects.filter(name__icontains=term)]
    return HttpResponse(json.dumps(entities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_entity_id(request):
    name = request.GET.get('name', '')
    if name:
        e = get_object_or_404(models.Entity, name=name)
        return HttpResponse(json.dumps({'id': e.id}), 'application/json')
    raise Http404


@user_passes_test(can_access)
def get_contact_name(request, contact_id):
    try:
        contact = models.Contact.objects.get(id=contact_id)
        return HttpResponse(json.dumps({'name': contact.get_name_and_entity()}), 'application/json')
    except models.Contact.DoesNotExist:
        return HttpResponse(json.dumps({'name': contact_id}), 'application/json')


def get_contacts_from_term(term):
    terms = [t.strip('()') for t in term.split(' ')]
        
    contacts = []
    contact_set = set()
    for i, term in enumerate(terms):
        x = list(models.Contact.objects.filter(
                Q(firstname__icontains=term) | Q(lastname__icontains=term) | Q(entity__name__icontains=term, entity__is_single_contact=False)
            ))
        if not x:
            contact_set = set()
            break
        if i == 0:
            contact_set = set(x)
        else:
            contact_set = contact_set.intersection(x)
        
    if not contact_set:
        for term in terms:
            queryset = models.Contact.objects.filter(
                Q(firstname__icontains=term) |
                Q(lastname__icontains=term) |
                Q(entity__name__icontains=term, entity__is_single_contact=False)
            )
            contacts += list(queryset)
        
    contacts = list(contact_set or set(contacts))
    contacts = [{'id': x.id, 'name': x.get_name_and_entity()} for x in contacts]
    contacts.sort(key = lambda x: x['name'])
    return contacts


@user_passes_test(can_access)
@log_error
def get_contact_id(request):
    name = request.GET.get('name')
    contacts = get_contacts_from_term(name)
    if len(contacts) != 1:
        raise Http404
    return HttpResponse(json.dumps({'id': contacts[0]['id']}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_contacts(request):
    term = request.GET.get('term')
    contacts = get_contacts_from_term(term)
    return HttpResponse(json.dumps(contacts), 'application/json')


@user_passes_test(can_access)
@popup_redirect
def edit_contact(request, contact_id, mini=True, go_to_entity=False):
    contact = get_object_or_404(models.Contact, id=contact_id)
    
    entity = contact.entity
    
    if request.method == 'POST':
        form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            contact = form.save()

            if go_to_entity:
                return HttpResponseRedirect(reverse('crm_view_entity', args=[contact.entity.id]))
            else:
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.ContactForm(instance=contact)
        
    return render_to_response(
        'Crm/edit_contact.html',
        {
            'form': form,
            'contact': contact,
            'entity': entity,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_contact(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    same_as_contact = None
    
    actions = contact.action_set.filter(archived=False)
    actions_by_set = get_actions_by_set(actions, 5)    
    
    request.session["redirect_url"] = reverse('crm_view_contact', args=[contact_id])
    
    if contact.same_as:
        same_as_contact = models.Contact.objects.filter(same_as=contact.same_as).exclude(id=contact.id)
    
    return render_to_response(
        'Crm/view_contact.html',
        {
            'contact': contact,
            'actions_by_set': actions_by_set,
            'same_as': same_as_contact,
            'entity': contact.entity
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_contact_actions(request, contact_id, action_set_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    if int(action_set_id):
        action_set_list = [get_object_or_404(models.ActionSet, id=action_set_id)]
    else:
        action_set_list = [None]
    
    request.session["redirect_url"] = reverse('crm_view_contact_actions', args=[contact_id, action_set_id])
    
    actions = contact.action_set.filter(archived=False).order_by("planned_date", "priority")
    actions_by_set = get_actions_by_set(actions, 0, action_set_list)    
    
    return render_to_response(
        'Crm/view_contact_actions.html',
        {
            'contact': contact,
            'actions_by_set': actions_by_set,
            'entity': contact.entity
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_entity_actions(request, entity_id, action_set_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    if int(action_set_id):
        action_set_list = [get_object_or_404(models.ActionSet, id=action_set_id)]
    else:
        action_set_list = [None]
    
    request.session["redirect_url"] = reverse('crm_view_entity_actions', args=[entity_id, action_set_id])
    
    actions = models.Action.objects.filter(Q(entities=entity) | Q(contacts__entity=entity),
        Q(archived=False)).distinct().order_by("planned_date", "priority")
    actions_by_set = get_actions_by_set(actions, 0, action_set_list)    
    
    return render_to_response(
        'Crm/view_entity_actions.html',
        {
            'actions_by_set': actions_by_set,
            'entity': entity
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_relationship(request, contact_id):
    contact1 = get_object_or_404(models.Contact, id=contact_id)
    if request.method == "POST":
        form = forms.AddRelationshipForm(contact1, request.POST)
        if form.is_valid():
            relationship = form.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact1.id]))
    else:
        form = forms.AddRelationshipForm(contact1)
    
    return render_to_response(
        'Crm/add_relationship.html',
        {'contact': contact1, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_relationship(request, contact_id, relationship_id):
    err_msg = ""
    try:
        contact = models.Contact.objects.get(id=contact_id)
    except models.Contact.DoesNotExist:
        contact = None
        err_msg = _(u"The contact doesn't exist anymore")
    
    try:
        relationship = models.Relationship.objects.get(id=relationship_id)
    except models.Relationship.DoesNotExist:
        err_msg = _(u"The relationship doesn't exist anymore")
    
    if err_msg:
        if contact:
            next_url = reverse("crm_view_contact", args=[contact.id])
        else:
            next_url = reverse('crm_board_panel')
        return render_to_response(
            'sanza/message_dialog.html',
            {
                'message': err_msg,
                'next_url':  next_url,
            },
            context_instance=RequestContext(request)
        )   
    else:
        if request.method == 'POST':
            form = forms.ConfirmForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["confirm"]:
                    relationship.delete()
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
        else:
            form = forms.ConfirmForm()
        return render_to_response(
            'sanza/confirmation_dialog.html',
            {
                'form': form,
                'message': _(u'Are you sure to delete the relationship "{0}"?').format(relationship),
                'action_url': reverse("crm_delete_relationship", args=[contact_id, relationship_id]),
            },
            context_instance=RequestContext(request)
        )


@user_passes_test(can_access)
@popup_redirect
def same_as(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    if request.method == "POST":
        form = forms.SameAsForm(contact, request.POST)
        if form.is_valid():
            if not contact.same_as:
                contact.same_as = models.SameAs.objects.create(main_contact=contact)
                contact.save()
            same_as_contact = form.cleaned_data['contact']
            same_as_contact.same_as = contact.same_as
            same_as_contact.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.SameAsForm(contact)
        if not form.has_choices():
            return render_to_response(
                'sanza/message_dialog.html',
                {
                    'title': _(u'SameAs contacts'),
                    'message': _(u"No homonymous for {0}").format(contact),
                    'next_url': reverse('crm_view_contact', args=[contact.id]),
                },
                context_instance=RequestContext(request)
            ) 
    
    return render_to_response(
        'Crm/same_as.html',
        {'contact': contact, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_same_as(request, current_contact_id, contact_id):
    current_contact = get_object_or_404(models.Contact, id=current_contact_id)
    contact = get_object_or_404(models.Contact, id=contact_id)
    if (not contact.same_as) or (not current_contact.same_as):
        raise Http404
    
    same_as = contact.same_as
    
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if same_as.contact_set.count()<=2:
                    for c in same_as.contact_set.all():
                        c.same_as = None
                        c.save()
                    # refresh
                    same_as = models.SameAs.objects.get(id=same_as.id)
                    same_as.delete()
                else:
                    if same_as.main_contact == contact:
                        if contact.id != current_contact_id:
                            same_as.main_contact = current_contact
                        else:
                            same_as.main_contact = None
                        same_as.save()
                    contact.same_as = None
                    contact.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[current_contact_id]))
    else:
        form = forms.ConfirmForm()
    confirm_message = _(u'Are you sure that "{0}" and "{1}" are not identical?').format(contact, current_contact)
    if same_as.contact_set.count() > 2 and same_as.main_contact == contact:
        confirm_message += _(u"\n\nNote: {0} is the main contact. This role will be transfered to {1}.").format(
            contact, current_contact
        )
        
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': confirm_message,
            'action_url': reverse("crm_remove_same_as", args=[current_contact_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_contact(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    contact = models.Contact(entity=entity)
    
    if request.method == 'POST':
        contact_form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if contact_form.is_valid():
            contact = contact_form.save()
            photo = contact_form.cleaned_data['photo']
            if photo != None:
                if type(photo) == bool:
                    contact.photo = None
                    contact.save()
                else:
                    contact.photo.save(photo.name, photo)
                    
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        contact_form = forms.ContactForm(instance=contact)
        
    return render_to_response(
        'Crm/edit_contact.html',
        {
            "entity": entity,
            "form": contact_form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
@log_error
def add_single_contact(request):
    if request.method == 'POST':
        contact = models.Contact()
        contact_form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if contact_form.is_valid():
            
            entity = models.Entity(
                name = contact.fullname,
                is_single_contact = True
            )
            entity.save()
            #This create a default contact
            default_contact = entity.default_contact
            
            contact = contact_form.save(commit=False)
            contact.entity = entity
            contact.save()
            
            default_contact.delete()
            contact.save() # change name of the entity

            contact_form.save_contact_subscriptions(contact)
            
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
        else:
            contact = None
    else:
        contact = None
        contact_form = forms.ContactForm()
        
    return render_to_response(
        'Crm/edit_contact.html',
        {
            'contact': contact,
            'form': contact_form,
            'is_single_contact': True,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_contact(request, contact_id):
    
    contact = get_object_or_404(models.Contact, id=contact_id)
    entity = contact.entity
    
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if contact.entity.is_single_contact:
                    contact.entity.delete()
                    return HttpResponseRedirect(reverse('crm_board_panel'))
                else:
                    contact.delete()
                    return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
            else:
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.ConfirmForm()
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the contact "{0}"?').format(contact),
            'action_url': reverse("crm_delete_contact", args=[contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def add_action_for_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    return select_contact_and_redirect(
        request,
        'crm_add_action_for_contact',
        'Crm/add_action.html',
        choices=entity.contact_set.filter(has_left=False)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action_for_contact(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    action = models.Action(contact=contact)
    if request.method == 'POST':
        form = forms.ActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_contact', args=[contact.id])    
            return HttpResponseRedirect(next_url)
        action = None
    else:
        opportunity_id = request.GET.get('opp_id', 0)
        initial = {}
        if opportunity_id:
            try:
                initial['opportunity'] = models.Opportunity.objects.get(id=opportunity_id)
            except models.Opportunity.DoesNotExist:
                pass
        form = forms.ActionForm(instance=action, initial=initial)
    
    context = {
        'form': form,
        'contact': contact,
    }
    
    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_entity_actions(request, entity_id, set_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    filters = []
    if int(set_id):
        action_set = get_object_or_404(models.ActionSet, id=set_id)
        filters.append(Q(type__set=action_set))
        title = action_set.name
    else:
        filters.append(Q(type__set=None))
        title = _(u"Other kind of actions") if models.ActionSet.objects.count() else _u("Actions")
    
    actions = models.Action.objects.filter(
        Q(entity=entity) | Q(contact__entity=entity) | Q(opportunity__entity=entity), *filters).order_by("planned_date", "priority")
    all_actions = True
    request.session["redirect_url"] = reverse('crm_entity_actions', args=[entity_id, set_id])
    return render_to_response(
        'Crm/entity_actions.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_contact_actions(request, contact_id, set_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    
    filters = []
    if int(set_id):
        action_set = get_object_or_404(models.ActionSet, id=set_id)
        filters.append(Q(type__set=action_set))
        title = action_set.name
    else:
        filters.append(Q(type__set=None))
        title = _(u"Other kind of actions") if models.ActionSet.objects.count() else _(u"Actions")
    
    actions = contact.action_set.filter(*filters).order_by("planned_date", "priority")
    all_actions = True
    request.session["redirect_url"] = reverse('crm_contact_actions', args=[contact_id, set_id])
    return render_to_response(
        'Crm/entity_actions.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_action(request, entity_id, contact_id):
    #entity_id or contact_id can be 0
    #add from menu -> both are 0 / add from contact -> entity_id = 0 / add from entity -> contact_id = 0
    contact_id = int(contact_id)
    entity_id = int(entity_id)
    contact = get_object_or_404(models.Contact, id=contact_id) if contact_id else None
    entity = get_object_or_404(models.Entity, id=entity_id) if entity_id else None
    
    if request.method == 'POST':
        form = forms.ActionForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url')
            action = form.save()
            if entity:
                action.entities.add(entity)
                if not next_url:
                    next_url = reverse("crm_view_entity", args=[entity.id])
            elif contact:
                action.contacts.add(contact)
                if not next_url:
                    next_url = reverse("crm_view_contact", args=[contact.id])
            else:
                action.display_on_board = True
            action.save()
            
            if not next_url:
                next_url = reverse('crm_board_panel')
            return HttpResponseRedirect(next_url)
    else:
        initial = {}
        if request.user.is_staff and request.user.first_name:
            initial['in_charge'] = request.user
        try:
            opp_id = int(request.GET.get('opportunity', 0))
            initial['opportunity'] = models.Opportunity.objects.get(id=opp_id)
        except (ValueError, models.Opportunity.DoesNotExist):
            pass
        
        form = forms.ActionForm(initial=initial)
    
    context = {
        'form': form,
        'contact_id': contact_id,
        'entity_id': entity_id,
    }
    
    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def edit_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.ActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url')
            if not next_url:
                next_url = reverse('crm_board_panel')
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionForm(instance=action)
    
    context = {
        'form': form,
        'action': action,
    }
    
    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url')
                
                if not next_url and action.entities.count():
                    next_url = reverse('crm_view_entity', args=[action.entities.all()[0].id])    
                
                if not next_url and action.contacts.count():
                    next_url = reverse('crm_view_contact', args=[action.contacts.all()[0].id])
                
                action.delete()
            
            return HttpResponseRedirect(next_url or reverse('sanza_homepage'))
    else:
        form = forms.ConfirmForm()
        
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete this action?'),
            'action_url': reverse("crm_delete_action", args=[action_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_entity_opportunities(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    opportunities = models.Opportunity.objects.filter(entity=entity)
    all_opportunities = True
    request.session["redirect_url"] = reverse('crm_entity_opportunities', args=[entity_id])
    return render_to_response(
        'Crm/entity_opportunities.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_opportunities(request, ordering=None):
    opportunities = models.Opportunity.objects.all()
    if not ordering:
        ordering = 'date'
    if ordering == 'name':
        opportunities = opportunities.order_by('name')
    elif ordering == 'status':
        opportunities = opportunities.order_by('status__ordering', 'status')
    elif ordering == 'type':
        opportunities = opportunities.order_by('type')
    elif ordering == 'date':
        opportunities = list(opportunities)
        opportunities.sort(key=lambda o: o.get_start_date() or datetime(1970, 1, 1))
        opportunities.reverse()
    
    request.session["redirect_url"] = reverse('crm_all_opportunities')
     
    all_opportunities = True
    request.session["redirect_url"] = reverse('crm_all_opportunities')
    return render_to_response(
        'Crm/all_opportunities.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def edit_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    
    if request.method == 'POST':
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity= form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_opportunity', args=[opportunity.id])   
            return HttpResponseRedirect(next_url)
    else:
        form = forms.OpportunityForm(instance=opportunity)
    
    return render_to_response(
        'Crm/edit_opportunity.html',
        {'opportunity': opportunity, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    actions = opportunity.action_set.filter(archived=False)
    actions_by_set = get_actions_by_set(actions)
    
    contacts = []
    for action in actions:
        contacts += [c for c in action.contacts.all()]
        for e in action.entities.all():
            contacts += [c for c in e.contact_set.filter(has_left=False)]
    contacts = list(set(contacts))
    contacts.sort(key=lambda x: x.lastname.lower())
    
    request.session["redirect_url"] = reverse('crm_view_opportunity', args=[opportunity.id])
    
    context = {
        'opportunity': opportunity,
        'actions_by_set': actions_by_set,
        'contacts': contacts,
    }
        
    return render_to_response(
        'Crm/view_opportunity.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                for a in opportunity.action_set.all():
                    a.opportunity = None
                    a.save()
                opportunity.delete()
                next_url = reverse('crm_board_panel')    
                return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('crm_view_opportunity', args=[opportunity.id]))
    else:
        form = forms.ConfirmForm()
                
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the opportunity "{0}"?').format(opportunity),
            'action_url': reverse("crm_delete_opportunity", args=[opportunity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_board_panel(request):
    return HttpResponseRedirect(reverse("users_favorites_list"))


@user_passes_test(can_access)
def view_all_actions(request):
    actions = models.Action.objects.all().order_by("-planned_date")
    partial = False
    multi_user = True
    default_my_actions = False
    all_actions = True
    view_name = "crm_all_actions"
    request.session["redirect_url"] = reverse('crm_all_actions')
    return render_to_response(
        'Crm/all_actions.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def do_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    if request.method =="POST":
        form = forms.ActionDoneForm(request.POST, instance=action)
        if form.is_valid():
            action = form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_board_panel')    
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionDoneForm(instance=action)
    return render_to_response(
        'Crm/do_action.html',
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def select_entity_and_redirect(request, view_name, template_name):
    if request.method == 'POST':
        form = forms.SelectEntityForm(request.POST)
        if form.is_valid():
            entity = form.cleaned_data["entity"]
            args = [entity.id]
            url = reverse(view_name, args=args)
            return HttpResponseRedirect(url)
    else:
        form = forms.SelectEntityForm()
    
    return render_to_response(
        template_name,
        {'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def select_contact_and_redirect(request, view_name, template_name, choices=None):
    opportunity_id = request.GET.get('opp_id', 0)
    url_args = "?opp_id={0}".format(opportunity_id) if opportunity_id else ""

    if request.method == 'POST':
        form = forms.SelectContactForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data["contact"]
            args = [contact.id]
            url = reverse(view_name, args=args)+url_args
            return HttpResponseRedirect(url)
    else:
        form = forms.SelectContactForm(choices=choices)
    
    post_url = reverse("crm_add_action")+url_args 
    
    return render_to_response(
        template_name,
        {'form': form, 'post_url': post_url},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_contact_to_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.SelectContactForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
            contact = form.cleaned_data["contact"]
            action.contacts.add(contact)
            action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectContactForm()
    
    return render_to_response(
        "Crm/add_contact_to_action.html",
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_contact_from_action(request, action_id, contact_id):
    action = get_object_or_404(models.Action, id=action_id)
    contact = get_object_or_404(models.Contact, id=contact_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
                action.contacts.remove(contact)
                action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you to remove {0} from this action?').format(contact),
            'action_url': reverse("crm_remove_contact_from_action", args=[action_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_entity_to_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.SelectEntityForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
            entity = form.cleaned_data["entity"]
            action.entities.add(entity)
            action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectEntityForm()
    
    return render_to_response(
        "Crm/add_entity_to_action.html",
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_entity_from_action(request, action_id, entity_id):
    action = get_object_or_404(models.Action, id=action_id)
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
                action.entities.remove(entity)
                action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you to remove {0} from this action?').format(entity),
            'action_url': reverse("crm_remove_entity_from_action", args=[action_id, entity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action_to_opportunity(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)

    if request.method == "POST":
        form = forms.SelectOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.cleaned_data["opportunity"]
            action.opportunity = opportunity
            action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])    
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectOpportunityForm()
    
    return render_to_response(
        'Crm/add_action_to_opportunity.html',
        {'action': action, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_action_from_opportunity(request, action_id, opportunity_id):
    action = get_object_or_404(models.Action, id=action_id)
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == "POST":
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if action.opportunity == opportunity:
                    action.opportunity = None
                    action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])    
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()
    
    
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to remove the action {0} from opportunity {1}?').format(
                action.subject, opportunity.name
            ),
            'action_url': reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity.id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_opportunity(request):
    next_url = request.session.get('redirect_url')
    if request.method == 'POST':
        opportunity = models.Opportunity()
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])    
            return HttpResponseRedirect(next_url)
        opportunity = None
    else:
        form = forms.OpportunityForm()
    
    next_url = next_url or reverse('crm_board_panel')    
    return render_to_response(
        'Crm/edit_opportunity.html',
        {'next_url': next_url, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action(request):
    return select_contact_and_redirect(
        request,
        'crm_add_action_for_contact',
        'Crm/add_action.html',
    )


@user_passes_test(can_access)
@popup_redirect
def edit_custom_fields(request, model_name, instance_id):
    try:
        form_class = {
            'entity': forms.EntityCustomFieldForm,
            'contact': forms.ContactCustomFieldForm,
        }[model_name]
    except KeyError:
        raise Http404
    
    instance = get_object_or_404(form_class.model(), id=instance_id)
    
    if request.method == 'POST':
        form = form_class(instance, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = form_class(instance)
    
    return render_to_response(
        'Crm/edit_custom_fields.html',
        {'form': form, 'instance': instance, 'model_name': model_name},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def new_contacts_import(request):
    if request.method == 'POST':
        instance = models.ContactsImport(imported_by=request.user)
        form = forms.ContactsImportForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            src = form.cleaned_data['import_file']
            ipt = form.save()
            if not ipt.name:
                ipt.name = os.path.splitext(src.name)[0]
                ipt.save()
            return HttpResponseRedirect(reverse('crm_confirm_contacts_import', args=[ipt.id]))
    else:
        form = forms.ContactsImportForm()
    
    return render_to_response(
        'Crm/new_contacts_import.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


def read_contacts(reader, fields, extract_from_email):
    contacts = []
    entity_dict = {}
    role_dict = {}
    groups_dict = {}
    for k, row in enumerate(reader):
        if k == 0:
            #remove the header row
            continue
        c = {}
        for i, field in enumerate(fields):
            try:
                c[field] = row[i]
            except IndexError:
                c[field] = ''
            if field == 'gender':
                if c[field]:
                    if c[field] in ('M', 'M.', 'Mr', 'Mr.'):
                        c[field] = models.Contact.GENDER_MALE
                    elif crm_settings.ALLOW_COUPLE_GENDER and c[field] in ('Mrs and Mr', 'Mme et M.'):
                        c[field] = models.Contact.GENDER_COUPLE
                    else:
                        c[field] = models.Contact.GENDER_FEMALE

            #Copy value of entity fields with _ rather than . for using it in template
            if field.find('.')>0:
                c[field.replace('.', '_')] = c[field]
            if field.find('city')>=0 and c[field]:
                field = field.replace('.', '_')
                #c[field+'_exists'] = (models.City.objects.filter(name__iexact=c[field]).count()>0)
            if field.find("accept_")==0:
                c[field] = True if c[field] else False
        
        c["entity_city_exists"] = check_city_exists(c["entity_city"], c["entity_zip_code"], c["entity_country"])
        c["city_exists"] = check_city_exists(c["city"], c["zip_code"], c["country"])
        
        if not any(c.values()):
            continue
        
        name = u"< {0} >".format(_(u"Unknown"))
        if not c['entity']:
            entity = u''
            if extract_from_email:
                res = re.match('(?P<name>.+)@(?P<cpn>.+)\.(?P<ext>.+)', c['email'])
                if res:
                    name, entity, ext = res.groups(0)
                    #email = u'{0}@{1}.{2}'.format(name, entity, ext)
                email_providers = (
                    'free', 'gmail', 'yahoo', 'wanadoo', 'orange', 'sfr', 'laposte',
                    'hotmail', 'neuf', 'club-internet', 'voila', 'aol', 'live'
                )
            c['entity'] = entity
        if not (c['lastname'] or c['firstname']):
            try:
                c['firstname'], c['lastname'] = [x.capitalize() for x in name.split('.')]
            except ValueError:
                c['lastname'] = name.capitalize()
        
        if c['entity']:
            c['entity_exists'] = (models.Entity.objects.filter(name__iexact=c['entity']).count()!=0) or \
                (c['entity'] in entity_dict)
            entity_dict[c['entity']] = True
        else:
            c['entity_exists'] = False
            
        if c['entity']:
            contact_qs = models.Contact.objects.filter(entity__name=c['entity'])
        else:
            contact_qs = models.Contact.objects.filter(entity__is_single_contact=True)
        c['contact_exists'] = (contact_qs.filter(
            lastname=c['lastname'], firstname=c['firstname']).count()!=0)
            
        if c['entity_type']:
            c['entity_type_exists'] = (models.EntityType.objects.filter(name=c['entity_type']).count()!=0)
        
        c['role'] = [x.strip() for x in c['role'].split(";") if x.strip()]
        c['role_exists'] = []
        for r in c['role']:
            c['role_exists'].append(
                (models.EntityRole.objects.filter(name__iexact=r).count()!=0) or (r.lower() in role_dict)
            )
            role_dict[r.lower()] = True
        c['roles'] = [{'name': r, 'exists': e} for (r, e) in zip(c['role'], c['role_exists'])]
        
        entity_groups = [x.strip() for x in c['entity.groups'].strip().split(";") if x]
        c['entity_groups'] = []
        for g in entity_groups:
            exists = (models.Group.objects.filter(name__iexact=g).count()!=0) or (g in groups_dict)
            groups_dict[g] = True
            c['entity_groups'].append({'name': g, 'exists': exists})
            
        contact_groups = [x.strip() for x in c['groups'].strip().split(";") if x]
        c['contact_groups'] = []
        for g in contact_groups:
            exists = (models.Group.objects.filter(name__iexact=g).count()!=0) or (g in groups_dict)
            groups_dict[g] = True
            c['contact_groups'].append({'name': g, 'exists': exists})
        
        contacts.append(c)
    total_contacts = k
    return contacts, total_contacts


def get_imports_fields():
    fields = [
        'gender', 'firstname', 'lastname', 'email', 'phone', 'mobile', 'job',
        'notes', 'role', 
        'accept_newsletter', 'accept_3rdparty',
        'entity', 'entity.type', 'entity.description', 'entity.website', 'entity.email',
        'entity.phone', 'entity.fax', 'entity.notes', 
        'entity.address', 'entity.address2', 'entity.address3',
        'entity.city', 'entity.cedex', 'entity.zip_code', 'entity.country',
        'address', 'address2', 'address3', 'city', 'cedex', 'zip_code', 'country',
        'entity.groups', 'groups',
    ]
    
    #custom fields
    custom_fields_count = models.CustomField.objects.all().aggregate(Max('import_order'))['import_order__max']
    if not custom_fields_count:
        custom_fields_count = 0
    for i in xrange(custom_fields_count):
        fields.append('cf_{0}'.format(i+1))
        
    custom_fields = []
    for idx in xrange(1, custom_fields_count+1):
        try:
            cf = models.CustomField.objects.get(import_order=idx)
            custom_fields.append(cf)
        except models.CustomField.DoesNotExist:
            custom_fields.append(None)
    
    return fields, custom_fields


@user_passes_test(can_access)
def contacts_import_template(request):
    fields, custom_fields = get_imports_fields()
    
    cols = fields[:len(fields)-len(custom_fields)] + custom_fields
    
    template_file = u";".join([u'"{0}"'.format(unicode(col)) for col in cols])+u"\n"
    
    return HttpResponse(template_file, content_type="text/csv", )


@user_passes_test(can_access)
def confirm_contacts_import(request, import_id):
    
    fields, custom_fields = get_imports_fields()
    
    custom_fields_count = len(custom_fields)
    cf_names = ['cf_{0}'.format(idx) for idx in xrange(1, custom_fields_count+1)]
    
    contacts_import = get_object_or_404(models.ContactsImport, id=import_id)
    if request.method == 'POST':
        form = forms.ContactsImportConfirmForm(request.POST, instance=contacts_import)
        
        if form.is_valid():
            
            reader = unicode_csv_reader(contacts_import.import_file, form.cleaned_data['encoding'], delimiter=form.cleaned_data['separator'])
            contacts, total_contacts = read_contacts(reader, fields, form.cleaned_data['entity_name_from_email'])
            default_department = form.cleaned_data['default_department']
            contacts_import = form.save()
            
            complex_fields = (
                'entity', 'city', 'entity.city', 'role', 'entity.groups',
                'contacts.groups', 'country', 'entity.country', 'entity.type',
            )

            if 'create_contacts' in request.POST:
                #create entities
                entity_dict = {}
                for c in contacts:
                    #Entity
                    if settings.DEBUG:
                        try:
                            print c['entity'], c['lastname']
                        except UnicodeError:
                            print '##!'
                            
                    entity_type = None
                    if not c['entity.type']:
                        entity_type = contacts_import.entity_type
                    else:
                        entity_type, _x =  models.EntityType.objects.get_or_create(name=c['entity.type'])
                            
                    if c['entity_exists']:
                        entity = models.Entity.objects.filter(name__iexact=c['entity'])[0]
                    else:
                        if c['entity']:
                            entity = models.Entity.objects.create(
                                name=c['entity'], type=entity_type, imported_by=contacts_import)
                        else:
                            entity, _x = models.Entity.objects.get_or_create(
                                contact__lastname=c['lastname'], contact__firstname=c['firstname'],
                                is_single_contact=True)
                            entity.name = u"{0} {1}".format(c['firstname'], c['lastname'])
                            entity.imported_by = contacts_import
                            entity.save()
                    
                    if entity.is_single_contact:
                        is_first_for_entity = True
                    else:
                        is_first_for_entity = not entity_dict.has_key(entity.name)
                        entity_dict[entity.name] = True
                    
                    for g in contacts_import.groups.all():
                        g.entities.add(entity)
                        g.save()
                        
                    #Contact
                    contact, _is_new = models.Contact.objects.get_or_create(
                        entity=entity, firstname=c['firstname'], lastname=c['lastname'])
                    contact.imported_by = contacts_import
                    
                    for field_name in fields:
                        if field_name in complex_fields:
                            continue
                        obj = contact
                        try:
                            x, field = field_name.split('.')
                            obj = getattr(obj, x)
                        except ValueError:
                            field = field_name
                        if c[field_name] and field!='city':
                            setattr(obj, field, c[field_name])
                    
                    if c['city']:
                        contact.city = resolve_city(c['city'], c['zip_code'], c['country'], default_department)
                    if c['entity.city']:
                        contact.entity.city = resolve_city(
                            c['entity.city'], c['entity.zip_code'], c['entity.country'], default_department
                        )
                    if c['role']:
                        for role_exists, role in zip(c['role_exists'], c['role']):
                            if role_exists:
                                contact.role.add(models.EntityRole.objects.filter(name__iexact=role)[0])
                            else:
                                contact.role.add(models.EntityRole.objects.create(name=role))
                    
                    for (is_entity, key) in ((True, 'entity_groups'), (False, 'contact_groups')):
                        for group_data in c[key]:
                            group, group_exists = group_data['name'], group_data['exists']
                            if group_exists:
                                group = models.Group.objects.filter(name__iexact=group)[0]
                            else:
                                group, _x = models.Group.objects.get_or_create(name=group)
                            if is_entity:
                                if contact.entity.is_single_contact:
                                    group.contacts.add(contact)
                                else:
                                    group.entities.add(contact.entity)
                            else:
                                group.contacts.add(contact)
                            group.save()
                    
                    contact.entity.save()
                    contact.save()
                    contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()
                    
                    for name, cf in zip(cf_names, custom_fields):
                        value = c[name]
                        if cf and value:
                            if cf.model == models.CustomField.MODEL_ENTITY and is_first_for_entity:
                                cfv, _x = models.EntityCustomFieldValue.objects.get_or_create(
                                    custom_field=cf, entity=contact.entity
                                )
                                cfv.value = value
                                cfv.save()

                            if cf.model == models.CustomField.MODEL_CONTACT:
                                cfv, _x = models.ContactCustomFieldValue.objects.get_or_create(custom_field=cf, contact=contact)
                                cfv.value = value 
                                cfv.save()
                return HttpResponseRedirect(reverse("sanza_homepage"))
            else:
                form = forms.ContactsImportConfirmForm(instance=contacts_import)
        else:
            
            reader = unicode_csv_reader(contacts_import.import_file, contacts_import.encoding, delimiter=contacts_import.separator)
            contacts, total_contacts = read_contacts(reader, fields, contacts_import.entity_name_from_email)
    else:
        reader = unicode_csv_reader(contacts_import.import_file, contacts_import.encoding, delimiter=contacts_import.separator)
        contacts, total_contacts = read_contacts(reader, fields, contacts_import.entity_name_from_email)
        form = forms.ContactsImportConfirmForm(instance=contacts_import)
    
    return render_to_response(
        'Crm/confirm_contacts_import.html',
        {'form': form, 'contacts': contacts, 'nb_contacts': len(contacts), 'total_contacts': total_contacts},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def get_group_name(request, gr_id):
    try:
        gr = models.Group.objects.get(id=gr_id)
        return HttpResponse(json.dumps({'name': gr.name}), 'application/json')
    except models.Group.DoesNotExist:
        return HttpResponse(json.dumps({'name': gr_id}), 'application/json')


@user_passes_test(can_access)
def get_groups(request):
    term = request.GET.get('term')
    queryset = models.Group.objects.filter(name__icontains=term)[:10]
    groups = [{'id': x.id, 'name': x.name} for x in queryset]
    return HttpResponse(json.dumps(groups), 'application/json')


@user_passes_test(can_access)
@log_error
def get_group_id(request):
    name = request.GET.get('name')
    try:
        gr = get_object_or_404(models.Group, name__iexact=name)
    except models.Group.MultipleObjectsReturned:
        gr = get_object_or_404(models.Group, name=name)
    return HttpResponse(json.dumps({'id': gr.id}), 'application/json')


def _toggle_object_bookmark(request, object_model, object_id):
    try:
        if request.is_ajax() and request.method == "POST":
            obj = get_object_or_404(object_model, id=object_id)
            obj.display_on_board = not obj.display_on_board
            obj.save()
            data = {'bookmarked': obj.display_on_board}
            return HttpResponse(json.dumps(data), 'application/json')
        raise Http404
    except:
        logger.exception("_toggle_object_bookmarked")


@user_passes_test(can_access)
def toggle_action_bookmark(request, action_id):
    return _toggle_object_bookmark(request, models.Action, action_id)


@user_passes_test(can_access)
def toggle_opportunity_bookmark(request, opportunity_id):
    return _toggle_object_bookmark(request, models.Opportunity, opportunity_id)


@user_passes_test(can_access)
@popup_redirect
def make_main_contact(request, current_contact_id, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    if not contact.same_as:
        raise Http404
    
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                contact.same_as.main_contact = contact
                contact.same_as.save()
        return HttpResponseRedirect(reverse('crm_view_contact', args=[current_contact_id]))
    else:
        form = forms.ConfirmForm()
        
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to make the contact {0} to be the default contact for this person?').format(contact),
            'action_url': reverse("crm_make_main_contact", args=[current_contact_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )


class ActionDocumentDetailView(EditableObjectView):
    model = models.ActionDocument
    edit_mode = False
    form_class = forms.ActionDocumentForm
    #varname = "action_doc"
    
    def get_object(self):
        action = get_object_or_404(models.Action, pk = self.kwargs['pk'])
        try:
            return action.actiondocument
        except self.model.DoesNotExist:
            warning_text = ""
            if not action.type:
                warning_text = _(u"The action has no type set: Unable to create the corresponding document")
            elif not action.type.default_template:
                warning_text = _(
                    u"The action type has no document template defined: Unable to create the corresponding document"
                )
            if warning_text:
                logger.warning(warning_text)
                user_message.warning(self.request, warning_text)
                raise Http404
            else:
                return self.model.objects.create(action=action, template=action.type.default_template)
    
    def get_template(self):
        return self.object.template


class ActionDocumentEditView(ActionDocumentDetailView):
    edit_mode = True


class ActionDocumentPdfView(PDFTemplateView):
    
    def find_template(self, template_type, action_type):
        potential_templates = []
        if action_type:
            action_type = slugify(action_type.name)
            potential_templates += [
                u"documents/_{0}_{1}.html".format(action_type, template_type),
            ]
        
        potential_templates += [
            "documents/_{0}.html".format(template_type),
        ]
        
        for template_name in potential_templates:
            try:
                find_template(template_name)
                return template_name
            except TemplateDoesNotExist:
                pass
        return ""
    
    def render_to_response(self, context, **response_kwargs):
        action = get_object_or_404(models.Action, pk=self.kwargs['pk'])
        try:
            doc = action.actiondocument
        except models.ActionDocument.DoesNotExist:
            raise Http404
        if not self.request.user.has_perm('can_view_object', doc):
            raise PermissionDenied
        context['to_pdf'] = True
        context['object'] = doc
        self.template_name = doc.template
        pdf_options_dict = getattr(settings, 'SANZA_PDF_OPTIONS', None)
        if pdf_options_dict is None:
            pdf_options = {'margin-top': 0, 'margin-bottom': 0, 'margin-right': 0, 'margin-left': 0, }
        else:
            pdf_options = pdf_options_dict.get(self.template_name, {})
        if self.cmd_options:
            self.cmd_options.update(pdf_options)
        else:
            self.cmd_options = pdf_options
        self.header_template = self.find_template("header", action.type)
        self.footer_template = self.find_template("footer", action.type)
        self.filename = slugify(u"{0}.contact - {0}.subject".format(action))+".pdf"
        return super(ActionDocumentPdfView, self).render_to_response(context, **response_kwargs)


class ActionArchiveView(object):
    
    def _get_selection(self, filter_value):
        try:
            values = {}
            for x in filter_value.split(","):
                pfx, val = x[0], int(x[1:])
                if pfx in values:
                    values[pfx].append(val)
                else:
                    values[pfx] = [val]
            return dict(values)
        except ValueError:
            raise Http404
    
    def get_queryset(self):
        values = self.request.GET.get("filter", None)
        qs = self.queryset
        if values and values!="null":
            values_dict = self._get_selection(values)
            
            selected_types = values_dict.get("t", [])
            if selected_types:
                if 0 in selected_types:
                    if len(selected_types) == 1:
                        #only : no types
                        qs = qs.filter(type__isnull=True)
                    else:
                        #combine no types and some types
                        qs = qs.filter(Q(type__isnull=True) | Q(type__in=selected_types))
                else:
                    #only some types
                    qs = qs.filter(type__in=selected_types)
            
            selected_users = values_dict.get("u", [])
            if selected_users:
                qs = qs.filter(in_charge__in=selected_users)
                
        return qs
        
    def get_context_data(self, *args, **kwargs):
        context = super(ActionArchiveView, self).get_context_data(*args, **kwargs)
        ats = models.ActionType.objects.all()
        in_charge = get_in_charge_users()
        values = self.request.GET.get("filter", None)
        if values and values!="null":
            context["filter"] = values
            values_dict = self._get_selection(values)
            
            selected_types = values_dict.get("t", [])
            for at in ats:
                if at.id in selected_types:
                    setattr(at, 'selected', True)
            if 0 in selected_types:
                context["no_type_selected"] = True
            
            selected_users = values_dict.get("u", [])
            for u in in_charge:
                if u.id in selected_users:
                    setattr(u, 'selected', True)
                    
        context["action_types"] = ats
        context["in_charge"] = in_charge
        return context
    
    def get_dated_queryset(self, **lookup_kwargs):
        date_field = self.get_date_field()
        
        dt1 = since = lookup_kwargs['%s__gte' % date_field]
        dt2 = until = lookup_kwargs['%s__lt' % date_field]
        
        l1 = Q(end_datetime__isnull=True) & Q(planned_date__gte=dt1) & Q(planned_date__lt=dt2)
        l2 = Q(end_datetime__isnull=False) & Q(planned_date__lt=dt2) & Q(end_datetime__gte=dt1)
        
        qs = self.get_queryset()
        return qs.filter(l1 | l2)
        
    def get(self, *args, **kwargs):
        self.request.session["redirect_url"] = self.request.path
        return super(ActionArchiveView, self).get(*args, **kwargs)

    
class ActionMonthArchiveView(ActionArchiveView, MonthArchiveView):
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    month_format ='%m'
    allow_future = True
    allow_empty = True

    
class ActionWeekArchiveView(ActionArchiveView, WeekArchiveView):
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    week_format = "%U"
    allow_future = True
    allow_empty = True


class ActionDayArchiveView(ActionArchiveView, DayArchiveView):
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    allow_future = True
    allow_empty = True
    month_format ='%m'


class NotPlannedActionArchiveView(ActionArchiveView, ListView):
    queryset = models.Action.objects.filter(planned_date=None).order_by("priority")
    template_name = "Crm/action_archive_not_planned.html"
