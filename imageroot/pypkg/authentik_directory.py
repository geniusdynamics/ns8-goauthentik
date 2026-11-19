# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

DOMAIN = "AUTHENTIK_NS8_LDAP_DOMAIN"
MATCHING = "AUTHENTIK_NS8_LDAP_MATCHING"
MANAGED = "AUTHENTIK_NS8_LDAP_MANAGED"
ADDITIONAL = "AUTHENTIK_NS8_LDAP_ADDITIONAL_DOMAINS"


def settings():
    import agent

    values = agent.read_envfile(Path(os.environ["AGENT_STATE_DIR"]) / "environment")
    return (
        values.get(DOMAIN, ""),
        values.get(MATCHING, "identifier"),
        values.get(ADDITIONAL, "").split(),
        values.get(MANAGED) == "True",
    )


def request_settings(request):
    domain, matching, additional, managed = settings()
    domain = request.get("ldap_domain", domain)
    return (
        domain,
        request.get("ldap_user_matching", matching),
        request.get("ldap_additional_domains", additional if domain else []),
        managed,
    )


def validation_failed(error):
    import agent

    agent.set_status("validation-failed")
    json.dump([{"field": "ldap_domain", "parameter": "ldap_domain", "value": "", "error": error}], sys.stdout)
    sys.exit(3)


class OverlappingRoots(Exception):
    pass


def directory_lock():
    import agent

    return agent.exclusive_file_lock(str(Path(os.environ["AGENT_STATE_DIR"]) / "ldap-configuration"))


def configure(request):
    with directory_lock():
        configure_sources(request)


def configure_sources(request):
    import agent

    domain, matching, additional, managed = request_settings(request)
    if not (domain or managed):
        return
    previous_domain, _, previous_additional, _ = settings()
    previous = ([previous_domain] if previous_domain else []) + previous_additional
    selected = ([domain] if domain else []) + additional
    # Binding populates ldapproxy credentials for the selected domains.
    agent.bind_user_domains(selected, check=True)
    try:
        apply_sources(domain, matching, additional, wait=True)
    except (OverlappingRoots, SystemExit) as error:
        agent.bind_user_domains(previous, check=True)
        if isinstance(error, OverlappingRoots):
            validation_failed("ldap_overlapping_roots")
        raise
    agent.mset_env({
        DOMAIN: domain,
        MATCHING: matching,
        ADDITIONAL: " ".join(additional),
        MANAGED: "True",
    })


def domains():
    from agent.ldapproxy import Ldapproxy

    proxy = Ldapproxy()
    return [
        {"name": name, "schema": info["schema"]}
        for name in sorted(proxy.get_domains_list())
        if (info := proxy.domains.get(name, {})).get("schema") in ("ad", "rfc2307")
    ]


def parameters(domain, matching):
    from agent.ldapproxy import Ldapproxy

    attrs = Ldapproxy().get_domain(domain)
    if not attrs or attrs.get("schema") not in ("ad", "rfc2307"):
        raise SystemExit("The selected NS8 LDAP domain is unavailable")
    key = hashlib.sha256(domain.encode()).hexdigest()[:16]
    ad = attrs["schema"] == "ad"
    return {
        "slug": "ns8-managed-ldap-" + key,
        "name": f"NS8 directory ({domain})",
        "domain_key": key,
        "server_uri": f"ldap://accountprovider:{int(attrs['port'])}",
        "bind_cn": attrs["bind_dn"],
        "bind_password": attrs["bind_password"],
        "base_dn": attrs["base_dn"],
        "user_object_filter": "(&(objectCategory=person)(objectClass=user))" if ad else "(objectClass=posixAccount)",
        "group_object_filter": "(objectClass=group)" if ad else "(objectClass=posixGroup)",
        "group_membership_field": "member" if ad else "memberUid",
        "user_membership_attribute": "distinguishedName" if ad else "uid",
        "object_uniqueness_field": "objectSid" if ad else "entryUUID",
        "user_matching_mode": matching,
        "username_mapping": (
            "authentik default Active Directory Mapping: sAMAccountName"
            if ad else "authentik default OpenLDAP Mapping: uid"
        ),
    }


def wait_ready():
    url = f"http://127.0.0.1:{int(os.environ['TCP_PORT'])}/-/health/ready/"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(60):
        try:
            with opener.open(url, timeout=3):
                return
        except urllib.error.URLError:
            time.sleep(2)
    raise SystemExit("Authentik did not become ready before directory reconciliation")


def apply_sources(domain, matching, additional, wait=False):
    if wait:
        wait_ready()
    attrs = [parameters(domain, matching)] if domain else []
    attrs.extend(parameters(name, "identifier") for name in additional)
    script = (Path(__file__).parent / "authentik_directory_runtime.py").read_text()
    payload = "params = " + repr(attrs) + "\n" + script
    # The bind password stays out of process arguments and task output.
    result = subprocess.run(
        ["podman", "exec", "-i", "goauthentik-app", "ak", "shell", "-c",
         "import sys; exec(sys.stdin.read())"],
        input=payload, text=True, capture_output=True,
    )
    if result.returncode == 23 and "ns8-ldap-overlapping-roots" in result.stdout.splitlines():
        raise OverlappingRoots()
    if result.returncode:
        raise SystemExit("Could not reconcile the NS8 LDAP sources in Authentik")


def reconcile():
    with directory_lock():
        domain, matching, additional, managed = settings()
        if domain or managed:
            try:
                apply_sources(domain, matching, additional)
            except OverlappingRoots:
                raise SystemExit("Enabled LDAP sources have overlapping directory roots") from None
