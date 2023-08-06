# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect, render
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic import (ListView, DetailView, UpdateView, CreateView,
        DeleteView, FormView)

from organizations.models import Organization
from organizations.mixins import (OrganizationMixin, OrganizationUserMixin,
        MembershipRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin)
from organizations.forms import (OrganizationForm, OrganizationUserForm,
        OrganizationUserAddForm, OrganizationAddForm, SignUpForm)
from organizations.utils import create_organization
from organizations.backends import invitation_backend, registration_backend
from organizations.utils import get_users_organizations, set_current_organization_to_session


class BaseOrganizationList(ListView):
    queryset = Organization.active.all()
    context_object_name = "organizations"

    def get_queryset(self):
        return super(BaseOrganizationList,
                self).get_queryset().filter(users=self.request.user)


@login_required
def switch_org(request):
    next = request.GET.get('next')
    organization_slug = request.GET.get('set_org')

    if organization_slug:
        try:
            organization = Organization.objects.get(users=request.user, slug=organization_slug)
        except ObjectDoesNotExist:
            raise(Http404)
        set_current_organization_to_session(request, organization)

        if next:
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect('/')

    organizations = get_users_organizations(request.user)
    if not organizations:
        raise Exception("No Organization Found for user: %s" % request.user)
    template_name = 'organizations/organization_switch.html'

    return render_to_response(template_name, {'organizations': organizations,
                                              'next': next,
                                             }, context_instance=RequestContext(request))


class BaseOrganizationDetail(OrganizationMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super(BaseOrganizationDetail, self).get_context_data(**kwargs)
        context['organization_users'] = self.organization.organization_users.all()
        context['organization'] = self.organization
        return context


class BaseOrganizationCreate(CreateView):
    model = Organization
    form_class = OrganizationAddForm
    template_name = 'organizations/organization_form.html'

    def get_success_url(self):
        return reverse("organization_list")

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BaseOrganizationUpdate(OrganizationMixin, UpdateView):
    form_class = OrganizationForm

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BaseOrganizationDelete(OrganizationMixin, DeleteView):
    def get_success_url(self):
        return reverse("organization_list")


class BaseOrganizationUserList(OrganizationMixin, ListView):
    def get(self, request, *args, **kwargs):
        self.organization = self.get_organization()
        self.object_list = self.organization.organization_users.all()
        context = self.get_context_data(object_list=self.object_list,
                organization_users=self.object_list,
                organization=self.organization)
        return self.render_to_response(context)


class BaseOrganizationUserDetail(OrganizationUserMixin, DetailView):
    pass


class BaseOrganizationUserCreate(OrganizationMixin, CreateView):
    form_class = OrganizationUserAddForm
    template_name = 'organizations/organizationuser_form.html'

    def get_success_url(self):
        return reverse('organization_user_list',
                kwargs={'organization_pk': self.object.organization.pk})

    def get_form_kwargs(self):
        kwargs = super(BaseOrganizationUserCreate, self).get_form_kwargs()
        kwargs.update({'organization': self.organization,
            'request': self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.organization = self.get_object()
        return super(BaseOrganizationUserCreate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.organization = self.get_object()
        return super(BaseOrganizationUserCreate, self).post(request, *args, **kwargs)


class BaseOrganizationUserRemind(OrganizationUserMixin, DetailView):
    template_name = 'organizations/organizationuser_remind.html'
    # TODO move to invitations backend?

    def get_object(self, **kwargs):
        self.organization_user = super(BaseOrganizationUserRemind, self).get_object()
        if self.organization_user.user.is_active:
            raise Http404(_("Already active")) # TODO add better error
        return self.organization_user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        invitation_backend().send_reminder(self.object.user,
                **{'domain': get_current_site(self.request),
                    'organization': self.organization, 'sender': request.user})
        return redirect(self.object)


class BaseOrganizationUserUpdate(OrganizationUserMixin, UpdateView):
    form_class = OrganizationUserForm


class BaseOrganizationUserDelete(OrganizationUserMixin, DeleteView):
    def get_success_url(self):
        return reverse('organization_user_list',
                kwargs={'organization_pk': self.object.organization.pk})


class OrganizationSignup(FormView):
    """
    View that allows unregistered users to create an organization account.

    It simply processes the form and then calls the specified registration
    backend.
    """
    form_class = SignUpForm
    template_name = "organizations/signup_form.html"
    # TODO get success from backend, because some backends may do something
    # else, like require verification
    backend = registration_backend()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('organization_add')
        return super(OrganizationSignup, self).dispatch(request, *args,
                **kwargs)

    def get_success_url(self):
        if hasattr(self, 'success_url'):
            return self.success_url
        return reverse('organization_signup_success')

    def form_valid(self, form):
        """
        """
        user = self.backend.register_by_email(form.cleaned_data['email'])
        create_organization(user=user, name=form.cleaned_data['name'],
                slug=form.cleaned_data['slug'], is_active=False)
        return redirect(self.get_success_url())


def signup_success(self, request):
    return render(request, "organizations/signup_success.html", {})


class OrganizationList(BaseOrganizationList):
    pass


class OrganizationCreate(BaseOrganizationCreate):
    """
    Allows any user to create a new organization.
    """
    pass


class OrganizationDetail(MembershipRequiredMixin, BaseOrganizationDetail):
    pass


class OrganizationUpdate(AdminRequiredMixin, BaseOrganizationUpdate):
    pass


class OrganizationDelete(OwnerRequiredMixin, BaseOrganizationDelete):
    pass


class OrganizationUserList(MembershipRequiredMixin, BaseOrganizationUserList):
    pass


class OrganizationUserDetail(AdminRequiredMixin, BaseOrganizationUserDetail):
    pass


class OrganizationUserUpdate(AdminRequiredMixin, BaseOrganizationUserUpdate):
    pass


class OrganizationUserCreate(AdminRequiredMixin, BaseOrganizationUserCreate):
    pass


class OrganizationUserRemind(AdminRequiredMixin, BaseOrganizationUserRemind):
    pass


class OrganizationUserDelete(AdminRequiredMixin, BaseOrganizationUserDelete):
    pass
