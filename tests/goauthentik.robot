*** Settings ***
Library    SSHLibrary

*** Variables ***
${HOST}    goauthentik.example.org
${SCENARIO}    install
${PREVIOUS_IMAGE}    ghcr.io/geniusdynamics/goauthentik:2.4.0
${PREVIOUS_CANDIDATE}    ghcr.io/geniusdynamics/goauthentik:authentik-2026-8
${LDAP_DOMAIN}    authentik-ci.example.org
${AD_DOMAIN}    authentik-ad.test
${ldap_id}    ${EMPTY}

*** Keywords ***
Node command
    [Arguments]    ${command}
    ${output}    ${error}    ${rc} =    Execute Command    ${command}    return_stderr=True    return_rc=True
    Should Be Equal As Integers    ${rc}    0    ${output} ${error}
    RETURN    ${output}

Authentik is ready
    Node command    curl -kfSs --resolve ${HOST}:443:127.0.0.1 https://${HOST}/-/health/ready/ >/dev/null

Remove directory fixture
    IF    $ldap_id
        Node command    remove-module --no-preserve ${ldap_id}
        Set Suite Variable    ${ldap_id}    ${EMPTY}
    END

Verify managed LDAP source lifecycle
    [Arguments]    ${domain}    ${membership_field}
    Node command    api-cli run module/${module_id}/configure-module --data '{"host":"${HOST}","http2https":true,"lets_encrypt":false,"ldap_domain":"${domain}"}'
    Node command
    ...    runagent -m ${module_id} podman exec goauthentik-app ak shell -c 'from authentik.sources.ldap.models import LDAPSource; source=LDAPSource.objects.get(managed__startswith="io.geniusdynamics/ns8-managed-ldap/", enabled=True); assert source.group_membership_field == "${membership_field}" and source.check_connection()["__all__"]["status"] == "ok"' >/dev/null
    Node command    api-cli run module/${module_id}/configure-module --data '{"host":"${HOST}","http2https":true,"lets_encrypt":false,"ldap_domain":""}'
    Node command
    ...    runagent -m ${module_id} podman exec goauthentik-app ak shell -c 'from authentik.sources.ldap.models import LDAPSource; assert not LDAPSource.objects.filter(managed__startswith="io.geniusdynamics/ns8-managed-ldap/", enabled=True).exists()' >/dev/null

*** Test Cases ***
Check if Authentik is installed correctly
    ${image} =    Set Variable If    '${SCENARIO}' == 'update'    ${PREVIOUS_IMAGE}    ${IMAGE_URL}
    IF    '${SCENARIO}' == 'update'
        ${available} =    Execute Command    podman manifest inspect ${image} >/dev/null 2>&1
        ...    return_rc=True    return_stdout=False
        IF    ${available} != 0
            ${image} =    Set Variable    ${PREVIOUS_CANDIDATE}
        END
    END
    ${output} =    Node command    add-module ${image} 1
    &{output} =    Evaluate    ${output}
    Set Suite Variable    ${module_id}    ${output.module_id}

Check if Authentik can be configured
    ${rc} =    Execute Command    api-cli run module/${module_id}/configure-module --data '{"host":"${HOST}","http2https":true,"lets_encrypt":false}'
    ...    return_rc=True  return_stdout=False
    Should Be Equal As Integers    ${rc}  0

Check if Authentik works as expected
    Wait Until Keyword Succeeds    5min    5s    Authentik is ready

Check if the previous release upgrades with its credentials and data
    Skip If    '${SCENARIO}' != 'update'
    ${before} =    Node command    runagent -m ${module_id} sha256sum database.env
    Node command    runagent -m ${module_id} podman exec goauthentik-app ak shell -c 'from authentik.core.models import Group; Group.objects.get_or_create(name="ns8-upgrade-fixture")' >/dev/null
    Node command    runagent -m ${module_id} podman exec goauthentik-app sh -c 'mkdir -p /data/media && echo persisted > /data/media/ns8-upgrade-fixture'
    Node command    api-cli run update-module --data '{"force":true,"module_url":"${IMAGE_URL}","instances":["${module_id}"]}'
    Wait Until Keyword Succeeds    5min    5s    Authentik is ready
    Node command    runagent -m ${module_id} podman exec goauthentik-app ak shell -c 'from authentik.core.models import Group; assert Group.objects.filter(name="ns8-upgrade-fixture").exists()' >/dev/null
    ${media} =    Node command    runagent -m ${module_id} podman exec goauthentik-app cat /data/media/ns8-upgrade-fixture
    Should Be Equal    ${media}    persisted
    ${after} =    Node command    runagent -m ${module_id} sha256sum database.env
    Should Be Equal    ${after}    ${before}

Check if Authentik uses persistent files and no Redis container
    Node command    runagent -m ${module_id} podman exec goauthentik-app test -d /data/media
    Node command    runagent -m ${module_id} sh -c '! podman container exists goauthentik-redis'

Check management of an NS8 OpenLDAP source
    [Teardown]    Remove directory fixture
    ${output} =    Node command    add-module ghcr.io/nethserver/openldap:2.8.1 1
    ${id} =    Evaluate    ast.literal_eval($output)['module_id']    ast
    Set Suite Variable    ${ldap_id}    ${id}
    Node command    api-cli run module/${ldap_id}/configure-module --data '{"provision":"new-domain","domain":"${LDAP_DOMAIN}","admuser":"admin","admpass":"Authentik-CI-2026"}'
    Verify managed LDAP source lifecycle    ${LDAP_DOMAIN}    memberUid

Check management of an NS8 Active Directory source
    [Teardown]    Remove directory fixture
    ${output} =    Node command    add-module ghcr.io/nethserver/samba:3.5.1 1
    ${id} =    Evaluate    ast.literal_eval($output)['module_id']    ast
    Set Suite Variable    ${ldap_id}    ${id}
    ${defaults} =    Node command    api-cli run module/${ldap_id}/get-defaults --data '{"provision":"new-domain"}'
    ${ipaddress} =    Evaluate    json.loads($defaults)['ipaddress_list'][0]['ipaddress']    json
    Node command
    ...    api-cli run module/${ldap_id}/configure-module --data '{"provision":"new-domain","realm":"${AD_DOMAIN}","nbdomain":"AUTHENTIKAD","hostname":"dc1","ipaddress":"${ipaddress}","adminuser":"administrator","adminpass":"Authentik-CI-2026"}'
    Verify managed LDAP source lifecycle    ${AD_DOMAIN}    member

Check if Authentik is removed correctly
    ${rc} =    Execute Command    remove-module --no-preserve ${module_id}
    ...    return_rc=True  return_stdout=False
    Should Be Equal As Integers    ${rc}  0
