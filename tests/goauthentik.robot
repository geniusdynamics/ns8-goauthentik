*** Settings ***
Library    SSHLibrary

*** Variables ***
${HOST}    goauthentik.example.org
${SCENARIO}    install
${PREVIOUS_IMAGE}    ghcr.io/geniusdynamics/goauthentik:2.0.1

*** Keywords ***
Node command
    [Arguments]    ${command}
    ${output}    ${error}    ${rc} =    Execute Command    ${command}    return_stderr=True    return_rc=True
    Should Be Equal As Integers    ${rc}    0    ${output} ${error}
    RETURN    ${output}

Authentik is ready
    Node command    curl -kfSs --resolve ${HOST}:443:127.0.0.1 https://${HOST}/-/health/ready/ >/dev/null

*** Test Cases ***
Check if Authentik is installed correctly
    ${image} =    Set Variable If    '${SCENARIO}' == 'update'    ${PREVIOUS_IMAGE}    ${IMAGE_URL}
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
    Node command    runagent -m ${module_id} podman exec goauthentik-app sh -c 'echo persisted > /media/ns8-upgrade-fixture'
    FOR    ${waypoint}    IN    2.0.3    2.1.0
        Node command    api-cli run update-module --data '{"force":true,"module_url":"ghcr.io/geniusdynamics/goauthentik:${waypoint}","instances":["${module_id}"]}'
        Wait Until Keyword Succeeds    5min    5s    Authentik is ready
        Node command    runagent -m ${module_id} podman exec goauthentik-app ak shell -c 'from authentik.core.models import Group; assert Group.objects.filter(name="ns8-upgrade-fixture").exists()' >/dev/null
        ${legacy_media} =    Node command    runagent -m ${module_id} podman exec goauthentik-app cat /media/ns8-upgrade-fixture
        Should Be Equal    ${legacy_media}    persisted
    END
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

Check if Authentik is removed correctly
    ${rc} =    Execute Command    remove-module --no-preserve ${module_id}
    ...    return_rc=True  return_stdout=False
    Should Be Equal As Integers    ${rc}  0
