# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
register = template.Library()
from datetime import date

from sanza.utils import logger
from django.db.models import Q
from sanza.Search.utils import get_date_bounds

@register.filter
def get_actions(contact, search_data):
    try:
        action_type = None
        planned_date = None
        done_date = None
        for search_block in search_data.values():
            for search_filter in search_block:
                if not action_type:
                    action_type = search_filter.get('action_type', None)
                if not planned_date:
                    planned_date = search_filter.get('action_by_planned_date', None)
                if not done_date:
                    done_date = search_filter.get('action_by_done_date', None)
        
        lookup_filter = []
        if action_type:
            lookup_filter += [Q(type=action_type)]
        if planned_date:
            dt_from, dt_to = get_date_bounds(planned_date)
            lookup_filter += [Q(planned_date__gte=dt_from) & Q(planned_date__lte=dt_to)]
        if done_date:
            dt_from, dt_to = get_date_bounds(done_date)
            lookup_filter += [Q(done_date__gte=dt_from) & Q(done_date__lte=dt_to)]
        if lookup_filter:
            return contact.action_set.filter(*lookup_filter)
        return contact.action_set.all()
    except:
        logger.exception("sanza_pdf.get_actions")
        raise


