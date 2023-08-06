# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.core.urlresolvers import reverse


from organizations.models import Organization
from organizations.utils import set_current_organization_to_session, get_current_organization


class OrganizationsMiddleware:
    """
    Simple Middleware that redirects all request to the switch_org view
    if no current_organization is stored in request.sesiion

    Skip the redirect by providing '?org=<slug>' as get parameter
    """

    def process_request(self, request):
        org_slug = request.GET.get('org')
        if org_slug:
            try:
                org = Organization.objects.get_for_user(request.user).get(slug=org_slug)
            except Organization.DoesNotExist:
                org = None

            if org:
                set_current_organization_to_session(request, org)

        current_organization = get_current_organization(request)
        if not request.path == reverse('organization_switch') and\
                not current_organization and request.user.is_authenticated():
            # skip the redirect and set current_organization if user is member of only one Organization
            url = reverse('organization_switch')
            url += "?next=%s" % request.path
            return redirect(url)

        return None
