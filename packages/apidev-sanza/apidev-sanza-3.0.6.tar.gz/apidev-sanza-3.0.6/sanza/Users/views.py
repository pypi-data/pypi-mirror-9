# -*- coding: utf-8 -*-

import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from sanza.permissions import can_access
from sanza.utils import logger
from sanza.Users import forms, models


class ToggleFavoriteException(Exception):
    """custom exception"""
    pass


@user_passes_test(can_access)
def toggle_favorite(request):
    """Add or remove a favorite"""
    try:
        if request.method == "POST":
            form = forms.UpdateFavoriteForm(request.POST)
            
            if form.is_valid():
                object_id = form.cleaned_data["object_id"]
                content_type = form.cleaned_data["content_type"]
                
                favorite, is_new = models.Favorite.objects.get_or_create(
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id
                )
                
                if not favorite.content_object:
                    favorite.delete()
                    raise ToggleFavoriteException(_(u'Invalid object'))
            
                label = getattr(favorite.content_object, 'name', unicode(favorite.content_object))
                if is_new:
                    data = {
                        'success': True,
                        'status': True,
                    }
                else:
                    favorite.delete()
                    data = {
                        'success': True,
                        'status': False,
                    }
            else:
                raise ToggleFavoriteException(u"{0}".format(form.errors))
        else:
            raise ToggleFavoriteException(u"POST expected")
    except ToggleFavoriteException:
        data = {'success': False, 'message': _(u'An error occured')}
        logger.exception("update_favorite")
    return HttpResponse(json.dumps(data), content_type="application/json")


@user_passes_test(can_access)
def list_favorites(request):
    """display the list of favorite items"""
    
    request.session["redirect_url"] = reverse('users_favorites_list')
    
    content_types = ContentType.objects.filter(user_favorite_set__user=request.user).distinct()
    
    favs_by_type = []
    for content_type in content_types:
        try:
            template_name = "Users/_section_favorites_{0}.html".format(content_type.model)
            get_template(template_name)
        except TemplateDoesNotExist:
            template_name = "Users/_section_favorites.html"
            
        favs_by_type.append(
            (
                content_type.model_class()._meta.verbose_name_plural.capitalize(),
                [
                    x.content_object
                    for x in models.Favorite.objects.filter(user=request.user, content_type=content_type)
                ],
                template_name,
            )
        )
        
    context = {
        'favs_by_type': favs_by_type,
    }
    
    return render_to_response(
        'Users/favorites_list.html',
        context,
        context_instance=RequestContext(request)
    )

@user_passes_test(can_access)
def user_homepage(request):
    """redirect to user homepage"""
    try:
        homepage = models.UserHomepage.objects.get(user=request.user)
        #Redirect to user homepage but make sure to avoid dead loop
        if homepage.url != reverse("sanza_homepage"):
            return HttpResponseRedirect(homepage.url)
    except models.UserHomepage.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('crm_board_panel'))


@user_passes_test(can_access)
def make_homepage(request):
    """Change the homepgae of the user"""
    if request.method == "POST":
        data = {"ok": False, "message": _(u"An error occured")}
        form = forms.UrlForm(request.POST)
        if form.is_valid():
            try:
                homepage = models.UserHomepage.objects.get(user=request.user)
                homepage.url = form.cleaned_data["url"]
                homepage.save()
            except models.UserHomepage.DoesNotExist:
                models.UserHomepage.objects.create(user=request.user, url=form.cleaned_data["url"])
            data["ok"] = True
        return HttpResponse(json.dumps(data), content_type="application/json")
    raise Http404

