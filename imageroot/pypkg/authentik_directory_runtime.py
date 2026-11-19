# SPDX-License-Identifier: GPL-3.0-or-later
"""Run within the pinned Authentik Django environment."""

from django.db import transaction
from django_tenants.utils import get_public_schema_name

from authentik.core.models import Source
from authentik.sources.ldap.models import LDAPSource, LDAPSourcePropertyMapping
from authentik.tenants.models import Tenant

OWNER = "io.geniusdynamics/ns8-managed-ldap"


def reconcile_directory(parameters):
    selected = parameters.copy()
    slug = selected.pop("slug", "")
    with transaction.atomic():
        if not slug:
            LDAPSource.objects.filter(managed=OWNER).update(enabled=False)
            return
        existing = Source.objects.filter(slug=slug).first()
        if existing and existing.managed != OWNER:
            raise ValueError("The requested LDAP source slug is already in use")

        username = selected.pop("username_mapping")
        domain_key = selected.pop("domain_key")
        mapping_name = f"NS8 LDAP group name ({domain_key})"
        mapping = LDAPSourcePropertyMapping.objects.filter(name=mapping_name).first()
        if mapping and mapping.managed != OWNER:
            raise ValueError("The requested LDAP mapping name is already in use")
        group_mapping, _ = LDAPSourcePropertyMapping.objects.update_or_create(
            name=mapping_name,
            defaults={
                "managed": OWNER,
                "expression": f'return {{"name": "ns8-{domain_key}-" + list_flatten(ldap.get("cn", ""))}}',
            },
        )
        source, _ = LDAPSource.objects.update_or_create(
            slug=slug,
            defaults={
                **selected, "managed": OWNER, "enabled": True, "start_tls": False,
                "sync_users": True, "sync_groups": True, "sync_users_password": False,
                "password_login_update_internal_password": False, "delete_not_found_objects": False,
            },
        )
        source.user_property_mappings.set(
            LDAPSourcePropertyMapping.objects.filter(name__in=[
                username, "authentik default LDAP Mapping: Name", "authentik default LDAP Mapping: mail",
            ])
        )
        source.group_property_mappings.set([group_mapping])
        LDAPSource.objects.filter(managed=OWNER).exclude(pk=source.pk).update(enabled=False)


tenant = Tenant.objects.get(ready=True, schema_name=get_public_schema_name())
with tenant:
    reconcile_directory(params)
