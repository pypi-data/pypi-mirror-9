# -*- coding: utf-8 -*-

from django.conf import settings
from organizations.utils import model_field_attr
from compat import get_user_model

User = get_user_model()


ORGS_INVITATION_BACKEND = getattr(settings, 'INVITATION_BACKEND',
        'organizations.backends.defaults.InvitationBackend')

ORGS_REGISTRATION_BACKEND = getattr(settings, 'REGISTRATION_BACKEND',
        'organizations.backends.defaults.RegistrationBackend')

ORGS_EMAIL_LENGTH = model_field_attr(User, 'email', 'max_length')
