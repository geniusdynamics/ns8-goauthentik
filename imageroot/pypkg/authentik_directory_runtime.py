# SPDX-License-Identifier: GPL-3.0-or-later
"""Run within the pinned Authentik Django environment."""

import re

from django.db import transaction
from django.db.models import Q
from django_tenants.utils import get_public_schema_name
from ldap3.utils.dn import parse_dn

from authentik.core.models import Source
from authentik.sources.ldap.models import LDAPSource, LDAPSourcePropertyMapping
from authentik.tenants.models import Tenant

OWNER = "io.geniusdynamics/ns8-managed-ldap"


def directory_root(base_dn):
    if not base_dn.strip():
        return ()
    parts = []
    rdn = []
    for attribute, value, separator in parse_dn(base_dn, strip=True):
        value = re.sub(
            r"\\(?:([0-9a-fA-F]{2})|(.))",
            lambda match: chr(int(match[1], 16)) if match[1] else match[2],
            value,
        )
        rdn.append((attribute.casefold(), value.casefold()))
        if separator != "+":
            parts.append(tuple(sorted(rdn)))
            rdn = []
    return tuple(reversed(parts))


def check_directory_roots(parameters, managed_sources):
    roots = [directory_root(entry["base_dn"]) for entry in parameters]
    manual_roots = [
        directory_root(base_dn)
        for base_dn in LDAPSource.objects.filter(enabled=True)
        .exclude(pk__in=managed_sources.values("pk")).values_list("base_dn", flat=True)
    ]
    for index, root in enumerate(roots):
        for other in roots[index + 1:] + manual_roots:
            length = min(len(root), len(other))
            if root[:length] == other[:length]:
                print("ns8-ldap-overlapping-roots")
                raise SystemExit(23)


def apply_source(parameters):
    selected = parameters.copy()
    slug = selected.pop("slug")
    domain_key = selected.pop("domain_key")
    owner = f"{OWNER}/{domain_key}"
    existing = Source.objects.filter(slug=slug).first()
    if existing and existing.managed not in (OWNER, owner):
        raise ValueError("The requested LDAP source slug is already in use")

    username = selected.pop("username_mapping")
    mapping_name = f"NS8 LDAP group name ({domain_key})"
    mapping = LDAPSourcePropertyMapping.objects.filter(name=mapping_name).first()
    if mapping and mapping.managed not in (OWNER, owner):
        raise ValueError("The requested LDAP mapping name is already in use")
    group_mapping, _ = LDAPSourcePropertyMapping.objects.update_or_create(
        name=mapping_name,
        defaults={
            "managed": owner,
            "expression": f'return {{"name": "ns8-{domain_key}-" + list_flatten(ldap.get("cn", ""))}}',
        },
    )
    source, _ = LDAPSource.objects.update_or_create(
        slug=slug,
        defaults={
            **selected, "managed": owner, "enabled": True, "start_tls": False,
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
    return source.pk


def reconcile_directory(parameters):
    managed_sources = LDAPSource.objects.filter(Q(managed=OWNER) | Q(managed__startswith=OWNER + "/"))
    with transaction.atomic():
        if len(parameters) > 1:
            check_directory_roots(parameters, managed_sources)
        selected_ids = [apply_source(entry) for entry in parameters]
        managed_sources.exclude(pk__in=selected_ids).update(enabled=False)


tenant = Tenant.objects.get(ready=True, schema_name=get_public_schema_name())
with tenant:
    reconcile_directory(params)
