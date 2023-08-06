# coding: utf-8

"""Declare relaydomains extension and register it."""

from django.utils.translation import ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import events, parameters


EXTENSION_EVENTS = [
    "RelayDomainCreated",
    "RelayDomainDeleted",
    "RelayDomainModified",
    "RelayDomainAliasCreated",
    "RelayDomainAliasDeleted",
    "ExtraRelayDomainForm",
    "FillRelayDomainInstances"
]


class AdminRelayDomains(ModoExtension):

    """Extension declaration."""

    name = "modoboa_admin_relaydomains"
    label = "Relay domains"
    version = "1.0.0"
    description = ugettext_lazy("Relay domains support for Postfix")
    url = "postfix_relay_domains"

    def load(self):
        from .app_settings import AdminParametersForm

        parameters.register(
            AdminParametersForm, ugettext_lazy("Relay domains")
        )
        events.declare(EXTENSION_EVENTS)
        from . import general_callbacks
        if exts_pool.is_extension_installed("modoboa_admin_limits"):
            from . import limits_callbacks
        if exts_pool.is_extension_installed("modoboa_amavis"):
            from . import amavis_callbacks

    def load_initial_data(self):
        """Create extension data."""
        from .models import Service
        for service_name in ['relay', 'smtp']:
            Service.objects.get_or_create(name=service_name)

        if not exts_pool.is_extension_installed("modoboa_admin_limits"):
            return
        from .limits_callbacks import create_new_limits
        create_new_limits()

exts_pool.register_extension(AdminRelayDomains)
