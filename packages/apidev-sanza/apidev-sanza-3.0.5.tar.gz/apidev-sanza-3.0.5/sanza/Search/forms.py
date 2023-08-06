# -*- coding: utf-8 -*-

from datetime import date, datetime
from itertools import chain
import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms import ChoiceField
from django.forms.util import flatatt
from django.template import Context
from django.template.loader import get_template
from django.utils import importlib
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _

import floppyforms as forms
from coop_cms.bs_forms import Form as BsForm

from sanza.Crm.models import Contact, Action, Group, Subscription, SubscriptionType
from sanza.Crm.widgets import OpportunityAutoComplete
from sanza.Search import models
from sanza.Search.widgets import DatespanInput
from sanza.Search.utils import get_date_bounds

SEARCH_FORMS = None


def load_from_name(constant_full_name):
    x = constant_full_name.split('.')
    constant_path, constant_name = '.'.join(x[:-1]), x[-1]
    module = importlib.import_module(constant_path)
    return getattr(module, constant_name)


class QuickSearchForm(BsForm):
    """Quick search form which is included in the menu"""
    text = forms.CharField(required=True,
        widget=forms.TextInput(attrs={'placeholder': _(u'Quick search')}))


def get_search_forms():
    global SEARCH_FORMS
    if not SEARCH_FORMS:
        SEARCH_FORMS = load_from_name(settings.SEARCH_FORM_LIST)
    return SEARCH_FORMS


def get_field_form(field):
    _forms = []
    for (cat, fs) in get_search_forms():
        _forms.extend(fs)
    x = dict([(f._name, f) for f in _forms if f])
    return x[field]


class GroupedSelect(forms.Select): 
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = '' 
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select {0}>'.format(flatatt(final_attrs))] 
        str_value = smart_unicode(value)
        for group_label, group in self.choices: 
            if group_label: # should belong to an optgroup
                group_label = smart_unicode(group_label) 
                output.append(u'<optgroup label="%s">' % escape(group_label)) 
            for k, v in group:
                option_value = smart_unicode(k)
                option_label = smart_unicode(v) 
                selected_html = (option_value == str_value) and u' selected="selected"' or ''
                output.append(u'<option value="%s"%s>%s</option>' % (escape(option_value), selected_html, escape(option_label))) 
            if group_label:
                output.append(u'</optgroup>')
        output.append(u'</select>') 
        return u'\n'.join(output)


class GroupedChoiceField(ChoiceField):
    def __init__(self, choices=(), required=True, widget=None, label=None, initial=None, help_text=None, *args, **kwargs):
        super(ChoiceField, self).__init__(required, widget, label, initial, help_text, *args, **kwargs)
        self.choices = choices
        
    def clean(self, value):
        """
        Validates that the input is in self.choices.
        """
        value = super(forms.ChoiceField, self).clean(value)
        if value in (None, ''):
            value = u''
        value = forms.util.smart_unicode(value)
        if value == u'':
            return value
        valid_values = []
        for group_label, group in self.choices:
            valid_values += [str(k) for k, v in group]
        if value not in valid_values:
            raise ValidationError(_(u'Select a valid choice. That choice is not one of the available choices.'))
        return value


class FieldChoiceForm(forms.Form):
    """The form for dynamicalling adding new filter"""
    
    def __init__(self, *args, **kwargs):
        super(FieldChoiceForm, self).__init__(*args, **kwargs)
        choices = [('', [('', '')])]#[('', [('', _(u'Please select a filter'))])]#1st line is just a label and can't be selected
        for (cat, fs) in get_search_forms():
            choices.append(
                (cat, [(reverse('search_get_field', args=[f._name]), f._label) for f in fs if f])
            )
        widget = GroupedSelect(attrs={
            'class': 'form-control half-width',
            'data-placeholder': _(u'Please select a filter'),
        })
        self.fields['field_choice'] = GroupedChoiceField(choices, widget=widget)

    def as_it_is(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row = u'%(field)s<span>%(help_text)s</span>',
            error_row = u'%s',
            row_ender = u'',
            help_text_html = u' <span class="helptext">%s</span>',
            errors_on_separate_row = False)


class SearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False,
        help_text=_('Enter a name and click save.'))
    
    class Media:
        css = {
            'all': ('chosen/chosen.css', 'chosen/chosen-bootstrap.css')
        }
        js = (
            'chosen/chosen.jquery.js',
        )
    
    excluded = forms.CharField(required=False, widget=forms.HiddenInput())
    #subject = forms.CharField(max_length=1000, required=False, widget=forms.HiddenInput())
    
    def __init__(self, data=None, instance=None, save=False, *args, **kwargs):
        super(SearchForm, self).__init__(data=data, *args, **kwargs)
        self._forms = {}
        self._instance = instance
        self._save = save
        self.contacts_display = False
        if instance: self.fields['name'].initial = instance.name
        if not data and instance:
            data = {}
            for gr in instance.searchgroup_set.all():
                for f in gr.searchfield_set.all():
                    key = '-_-'.join((gr.name, f.field, str(f.count or len(data))))
                    if f.is_list:
                        #data[key] = json.loads(f.value) # doesn't work :(
                        data[key] = self._str_to_list(f.value)
                    else:
                        data[key] = f.value
        if data:
            for key in data:
                if hasattr(data, 'getlist'):
                    value = data.getlist(key)
                    if len(value)==1:
                        value = data.get(key)
                else:
                    value = data.get(key)
                try:
                    #extract search fields
                    gr, field, fid = key.split('-_-')
                    fid = int(fid) #will raise an except for city visible field --> ignore this field
                    if not self._forms.has_key(gr):
                        self._forms[gr] = []
                    form_class = get_field_form(field)
                    form = form_class(gr, fid, {field: value})
                    self.contacts_display = self.contacts_display or form._contacts_display
                    self._forms[gr].append(form)
                except ValueError:
                    pass
                except Exception, msg:
                    print "Oups", msg
            #sort forms of a group according to their id
            for fs in self._forms.values(): 
                fs.sort(key=lambda f: f._count)
    
    def block_count(self):
        return len(self._forms)
    
    def field_count(self):
        return sum([len(f) for f in self._forms])
    
    def _str_to_list(self, str_value):
        def _split_unicode(x):
            x0 = x
            try:
                if x[:2] in ("u'", 'u"'):
                    x = x[2:]
                elif x[0] in ("'", '"'):
                    x = x[1:]
                
                if x[-1] in ("'", '"'):
                    x = x[:-1]
            except IndexError:
                return x0
            return x
            
        if str_value[0] == '[' and str_value[-1] == ']':
            values = str_value[1:-1] #remove [ and ]
            values = values.split(", ") # get things separated by ', '
            values = [x for x in values]
            values =  [_split_unicode(x) for x in values]
            return values
        return []
    
    def serialize(self):
        data = {}
        for group, forms in self._forms.items():
            for form in forms:
                if group in data:
                    data[group] += [form.serialize()]
                else:
                    data[group] = [form.serialize()]
        return data
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if self._save:
            if name:
                qs = models.Search.objects.filter(name=name)
                if self._instance and self._instance.id:
                    qs = qs.exclude(id=self._instance.id)
                if qs.count()>0:
                    raise ValidationError("This search name is already used")
            else:
                if self._instance:
                    raise ValidationError("A name is required for saving the search")
        return name
    
    def clean(self):
        keys = self._forms.keys()
        keys.sort()
        cleaned_data = super(SearchForm, self).clean()
        for key in keys:
            for form in self._forms[key]:
                cleaned_data.update(form.clean())
        return cleaned_data
    
    def save_search(self):
        self._instance.searchgroup_set.all().delete()
        self._instance.name = self.cleaned_data['name']
        self._instance.save()
        keys = self._forms.keys()
        for key in keys:
            gr = models.SearchGroup.objects.create(name=key, search=self._instance)
            for form in self._forms[key]:
                field = models.SearchField.objects.create(
                    search_group=gr, field=form._name, value=form._value, count=form._count)
                if form.multi_values:
                    field.is_list = True
                    field.save()
        return self._instance
    
    def clean_excluded(self):
        excluded = self.cleaned_data['excluded']
        if excluded:
            return [int(x) for x in excluded.strip("#").split("##")]
        return []

    def is_valid(self):
        if not super(SearchForm, self).is_valid():
            return False
        keys = self._forms.keys()
        keys.sort()
        results = []
        for key in keys:
            lookup = {}
            for form in self._forms[key]:
                if not form.is_valid():
                    return False
        return True
    
    def _get_contacts(self):
        keys = self._forms.keys()
        keys.sort()
        contacts = set([])
        global_post_processors = []
        self.contains_refuse_newsletter = False
        
        for key in keys:
            post_processors = []
            contacts_set = Contact.objects.all()
            
            if not ('secondary_contact' in [f._name for f in self._forms[key]]):
                contacts_set = contacts_set.filter(main_contact=True)
            
            for form in self._forms[key]:
                
                contacts_set = form.get_queryset(contacts_set)
                
                if hasattr(form, 'post_process'):
                    post_processors.append(form.post_process)
                    
                if hasattr(form, 'global_post_process'):
                    global_post_processors.append(form.global_post_process)

            for pp in post_processors:
                contacts_set = pp(contacts_set)
                
            contacts = contacts.union(set(contacts_set))
        
        for gpp in global_post_processors:
            contacts = gpp(contacts)

        #Just for compatibility
        queryset = SubscriptionType.objects.filter(site=Site.objects.get_current(), name=u'Newsletter')
        if queryset.count():
            for contact in contacts:
                for subscription_type in queryset:
                    try:
                        if not contact.subscription_set.get(subscription_type=subscription_type).accept_subscription:
                            self.contains_refuse_newsletter = True
                            break
                    except Subscription.DoesNotExist:
                        self.contains_refuse_newsletter = True
                        break
                
        return list(contacts)
    
    def _get_filter_func(self):
        form_names = [f._name for f in chain.from_iterable(self._forms.values())]
        if 'contact_has_left' in form_names:
            return lambda c: c
        return lambda c: c and (not c.has_left)

    def get_contacts_by_entity(self):
        contacts = self._get_contacts()
        contacts_count = 0
        entities = {}
        filter_func = self._get_filter_func()
        empty_entities = {}
        for contact in contacts:
            pass_filter = filter_func(contact)
            entity = contact.entity if contact else None
            if entity and not entities.has_key(entity.id):
                entities[entity.id] = (entity, [])
                empty_entities[entity.id] = entity
            if pass_filter:
                entities[entity.id][1].append(contact)
                entities[entity.id][1].sort(key=lambda c: c.lastname.lower())
                empty_entities.pop(entity.id, None)
                contacts_count += 1
            
        results = []
        for entity, contacts in entities.values():
            entity.search_contacts = contacts
            if entity.id in empty_entities:
                setattr(entity, 'is_empty', True)
            results.append(entity)
        results.sort(key=lambda x: x.name)
        return results, contacts_count, (len(empty_entities)>0)
    
    def get_contacts(self):
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        ids = self.cleaned_data['excluded']
        return [c for c in contacts if (c.id not in ids and filter_func(c))]
        
    def get_contacts_emails(self):
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        excluded_ids = self.cleaned_data['excluded']
        emails = []
        for c in contacts:
            if c.get_email and (c.id not in excluded_ids) and filter_func(c):
                if c.firstname or c.lastname:
                    emails.append(u'"{1}" <{0}>'.format(c.get_email, c.fullname))    
                else:
                    emails.append(c.get_email)
        return emails
    
    def actions(self):
        f = FieldChoiceForm()
        return u"""
            {0}
            <a class="btn btn-xs btn-default btn-yellow add-field" href=""><span class="glyphicon glyphicon-filter"></span> {1}</a>
            <a class="btn btn-xs btn-default add-block" href=""><span class="glyphicon glyphicon-th-list"></span> {2}</a>
            <a class="btn btn-xs btn-default duplicate-block" href=""><span class="glyphicon glyphicon-share"></span> {5}</a>
            <a class="btn btn-xs btn-danger clear-block" href=""><span class="glyphicon glyphicon-remove"></span> {3}</a>
            <a class="btn btn-xs btn-danger remove-block" href=""><span class="glyphicon glyphicon-trash"></span> {4}</a>""".format(
                f.as_it_is(), _(u'Add filter'), _(u'Add block'), _(u'Clear'), _(u'Remove'), _(u'Duplicate'))
    
    def as_html(self):
        keys = self._forms.keys()
        keys.sort()
        html = u'<div>{0}</div>'.format(self.as_p())
        if keys:
            for key in keys:
                html += u'<div class="search-block" rel="{0}"><div class="actions">{1}</div><div class="fields">'.format(key, self.actions())
                for form in self._forms[key]:
                    html += form.as_it_is()
                html += '</div></div>'
        return html


class SearchFieldForm(BsForm):
    _contacts_display = False
    multi_values = False
    
    def __init__(self, block, count, data=None, *args, **kwargs):
        self._block = block
        self._count = count
        form_data = None
        if data:
            if self.multi_values:
                val = data[self._name]
                self._value = val if type(val) is list else [val]
            else:
                self._value = data[self._name]
            form_data = {self._get_field_name(): self._value}
        super(SearchFieldForm, self).__init__(form_data, *args, **kwargs)
        
    def _get_field_name(self):
        return self._block+'-_-'+self._name+'-_-'+unicode(self._count)
        
    def _add_field(self, field):
        field.required = True
        if not field.widget.attrs.get('class', None):
            field.widget.attrs['class'] = "form-control"
        else:
            field.widget.attrs['class'] += " form-control"
        self.fields[self._get_field_name()] = field
        
    def clean(self):
        return {self._get_field_name(): self._value}
        
    def serialize(self):
        return {self._name: self._value}
        
    def as_it_is(self):
        t = get_template("Search/_search_field_form.html")
        return t.render(Context({"form": self}))
    
    def get_queryset(self, qs):
        if hasattr(self, 'get_lookup'):
            lookup = self.get_lookup()
            if lookup:
                if type(lookup) is dict:
                    qs = qs.filter(**lookup)
                elif type(lookup) is list:
                    qs = qs.filter(*lookup)
                else:
                    qs = qs.filter(lookup)
                    
        if hasattr(self, 'get_exclude_lookup'):
            lookup = self.get_exclude_lookup()
            if lookup:
                if type(lookup) is dict:
                    qs = qs.exclude(**lookup)
                elif type(lookup) is list:
                    qs = qs.exclude(*lookup)
                else:
                    qs = qs.exclude(lookup)
        return qs


class TwoDatesForm(SearchFieldForm):
    
    def __init__(self, *args, **kwargs):
        super(TwoDatesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label, initial='{0} {0}'.format(date.today().strftime("%d/%m/%Y")),
            widget=DatespanInput())
        self._add_field(field)
        
    def __getattr__(self, name):
        if name == 'clean_'+self._get_field_name():
            return self._clean_field
        return super(TwoDatesForm, self).__getattr__(name)
    
    def _clean_field(self):
        try:
            self._get_dates()
        except ValueError:
            raise ValidationError(_(u"Two valid dates are required"))
        return self._value
    
    def _get_dates(self):
        return get_date_bounds(self._value)


class YesNoSearchFieldForm(SearchFieldForm):
    def __init__(self, *args, **kwargs):
        super(YesNoSearchFieldForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Yes')), (0, _('No')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
    
    def is_yes(self):
        return True if int(self._value) else False


class SearchActionBaseForm:
    def _pre_init(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        return initial_contacts
        
    def _post_init(self, initial_contacts):
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts

    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        contacts = Contact.objects.filter(id__in=ids)
        #contact_by_ids = {unicode(c.id): c for c in contacts}
        contact_by_ids = {}
        for c in contacts:
            contact_by_ids[unicode(c.id)] = c
        ordered_contacts = []
        for cid in ids:
            ordered_contacts.append(contact_by_ids[cid])
        return ordered_contacts


class SearchActionForm(forms.Form, SearchActionBaseForm):
    contacts = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        initial_contacts = self._pre_init(*args, **kwargs)
        super(SearchActionForm, self).__init__(*args, **kwargs)
        self._post_init(initial_contacts)


class ContactsAdminForm(SearchActionForm):
    subscribe_newsletter = forms.BooleanField(required=False)


class PdfTemplateForm(SearchActionForm):
    search_dict = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(PdfTemplateForm, self).__init__(*args, **kwargs)
        
        if getattr(settings, 'SANZA_PDF_TEMPLATES', None):
            choices = settings.SANZA_PDF_TEMPLATES
        else:
            choices = SANZA_PDF_TEMPLATES = (
                ('pdf/labels_24.html', _(u'etiquettes 24')),
                ('pdf/labels_21.html', _(u'etiquettes 21')),
                ('pdf/agipa_21.html', _(u'Agipa 21')),
                ('pdf/labels_16.html', _(u'etiquettes 16')),
                ('pdf/address_strip.html', _(u'bande adresse')),
            )
        
        self.fields['template'] = ChoiceField(
            choices=choices, required=True, label=_(u'template'),
            help_text=_(u'Select the type of document to generate')
        )
        
        extra_fields = getattr(settings, 'SANZA_PDF_FORM_EXTRA_FIELDS', None)
        if extra_fields:
            for field_name, field_label, initial_value in extra_fields:
                self.fields[field_name] = forms.CharField(label=field_label, initial=initial_value)
       
    def patch_context(self, context):
        template = self.cleaned_data['template']
        extra_data = self._get_extra_data()
        context.update(extra_data)
        hooks = getattr(settings, 'SANZA_PDF_FORM_CONTEXT_HOOKS', {})
        if hooks and hooks.has_key(template):
            context = hooks[template](template, context)
        return context
    
    def _get_extra_data(self):
        #This extra_data comes from additional fields defined in SANZA_PDF_FORM_EXTRA_FIELDS settings
        #These values are passed to the template
        extra_data = dict(self.cleaned_data)
        for f in ('template', 'contacts', 'search_dict'):
            extra_data.pop(f)
        return extra_data
        
        
class ActionForContactsForm(forms.ModelForm):
    date = forms.DateField(label=_(u"planned date"), required=False, widget=forms.TextInput())
    time = forms.TimeField(label=_(u"planned time"), required=False)
    contacts = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Action
        fields = ('date', 'time', 'type', 'subject', 'in_charge', 'detail',
            'planned_date', 'contacts', 'opportunity')
        
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(ActionForContactsForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
        self.fields['opportunity'].widget = OpportunityAutoComplete(
            attrs={'placeholder': _(u'Enter the name of an opportunity'), 'size': '80', 'class': 'colorbox'})
        
    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return Contact.objects.filter(id__in=ids)
        
    def clean_planned_date(self):
        d = self.cleaned_data["date"]
        t = self.cleaned_data.get("time", None)
        if d:
            return datetime.combine(d, t or datetime.min.time())
        return None


class GroupForContactsForm(forms.Form):
    contacts = forms.CharField(widget=forms.HiddenInput())
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())
    on_contact = forms.BooleanField(label=_(u"Group on contact"), required=False, initial=True,
        help_text=_(u"Define if the group is added on the contact itself or on his entity"))
    
    class Media:
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )
        
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(GroupForContactsForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
    
        self.fields['groups'].widget.attrs = {
            'class': 'chzn-select',
            'data-placeholder': _(u'Select groups'),
            'style': "width:350px;"
        }
        self.fields['groups'].help_text = ''

    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return Contact.objects.filter(id__in=ids)


class SearchNameForm(forms.Form):
    search_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    name = forms.CharField(required=True, label=_(u"Name"))
    search_fields = forms.CharField(required=True, widget=forms.HiddenInput())
    
    def clean_name(self):
        search_id = self.cleaned_data["search_id"]
        
        name = self.cleaned_data["name"]
        if not name:
            raise ValidationError(_(u"This field is required"))
        
        qs = models.Search.objects.filter(name=name)
        if search_id:
            qs = qs.exclude(id=search_id)
        if qs.count()>0:
            raise ValidationError(_(u"This name is already used"))
        
        if search_id:
            search = models.Search.objects.get(id=search_id)
            if search.name != name:
                search.name = name
                search.save()
        else:
            search = models.Search(name=name)        
        return search
    
    def clean_search_fields(self):
        search_fields = self.cleaned_data["search_fields"]
        data = json.loads(search_fields)
        for k in ('csrfmiddlewaretoken', 'excluded', 'name', 'field_choice'):
            data.pop(k, None)
        return data
