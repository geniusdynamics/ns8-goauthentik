# Authentik and NS8 single sign-on

This guide covers what administrators can use today and the work needed for native NS8 OIDC registration with Authentik. The NS8 SSO interface and application integrations are still evolving. This review was made on **19 November 2026**. The references at the end identify the upstream revisions used for the review. Check the installed application and the current upstream contract before applying a workaround or implementing an adapter.

## What works today

A user domain, a login provider, and an application are separate parts of the deployment.

| Need | Supported path |
| --- | --- |
| Use NS8 directory accounts in Authentik | Configure an OpenLDAP or Samba AD user domain as a managed LDAP source in the Authentik module. The directory integration also supports optional additional NS8 domains on the branch introducing this feature. |
| Keep an LDAP source created with the old community instructions | Keep the source in Authentik. Directory integration is opt-in. Follow the migration guide if you want NS8 to take over the source while retaining existing accounts. |
| Use Authentik for a specific app | Register an OIDC application and client in Authentik and use the app's manual OIDC settings, if the installed app version offers them. |
| Use the cluster provider picker and automatic client registration | Use a provider supported by that consumer, such as the Keycloak-based `ns8-idp` reference where the provider and consumer are available for your versions. |
| Use a federated cloud identity as an NS8 directory account | The reference module has an Entra ID provisioning path for internal Samba AD. Authentik directory sync imports identities into Authentik. Automatic creation of an NS8 AD or OpenLDAP account is a separate feature. |

The managed LDAP source appears in Authentik under **Directory → Federation and Social login**. LDAP sync lets Authentik recognize directory users. A consuming app still needs its own OIDC or SAML configuration. The Authentik module's native NS8 OIDC advertisement, automatic client registration, and cleanup are future work. [Directory setup and migration](ns8-directory-login.md) · [NS8 architecture issue](https://github.com/NethServer/dev/issues/8080)

## Where the current contract fits

At the reviewed revision, NS8 discovers a provider through the Redis service record `module/{MODULE_ID}/srv/http/oidc` and its `service-oidc-changed` event. The provider advertises `host` and `issuer_url_prefix`. Consumers append the user-domain name to that prefix to obtain the realm issuer. The client binds to that domain and calls `register-client` under the provider module's `clientadm` ACL. Registration returns the client ID, secret, realm, and exact issuer. It can also configure login and logout redirect URIs, web origins, additional audiences, and secret rotation. [NS8 developer manual at the reviewed revision](https://github.com/NethServer/ns8-core/blob/f0c4084473f2a75c0f226d77b413c872434bc61f/docs/core/user_domains.md#single-sign-on)

The reference implementation already supplies one Keycloak realm per domain, LDAP federation, client ownership checks, secret reuse and rotation, preservation of a disabled client, and cleanup when an application is removed or unbound. It reconciles on cluster events and at service startup to recover from missed events. Those are requirements to carry across to another provider. The record is a discovery hint. Consumers still need to handle an endpoint that is starting, temporarily unreachable, or reconfigured after the last event. [Reference module and operating model](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/README.md) · [Registration implementation](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/imageroot/actions/register-client/20register)

## Gaps and workarounds

| Gap or limitation | Impact | Workaround today |
| --- | --- | --- |
| Discovery assumes a realm issuer per user domain. Authentik's default issuer is based on an application slug. Its global issuer mode uses the host root, with discovery still served under each application. | A made-up `issuer_url_prefix` can make a consumer offer a provider whose discovery document and token issuer it cannot validate. Setting Authentik to global mode alone does not satisfy the current NS8 contract. | Use manual OIDC with the exact issuer from the Authentik application's discovery document, or use the supported realm-based provider in the NS8 picker. |
| Authentik's NS8 module currently implements LDAP source management. Automatic OIDC client creation, rotation and removal are separate. | LDAP setup alone does not give an app an OIDC client or manage its credentials. | Create an Authentik client per app. Record ownership and callback URLs, rotate the secret at both ends, and revoke the client when retiring an app. |
| Client support varies by application and version. A working browser SSO login also says little about application APIs or desktop and mobile clients. | An app can lack a manual issuer field, an identity mapping it needs, or support for the available logout flow. | Use a tested manual path only where the installed version supports it. For other apps, keep the existing password, LDAP, app-password or supported SAML path. Check each client type separately. |
| The common `preferred_username` claim is a name. The reference module also maps `ldap_uuid` for consumers that need a directory identity key, including Nextcloud. Authentik's internal LDAP matching identifiers and OIDC `sub` are separate concepts. | Changing issuer, subject mode or mapping can create a second app account, attach an existing account incorrectly, or lose group-based access. | Inventory the current issuer, app account ID, subject or LDAP UID, groups and claims. Use the app's verified account-linking procedure and a small pilot. Keep the old sign-in path until fresh logins and access checks pass. |
| The reference module documents automatic provisioning from its federated IdP into internal Samba AD. Its OpenLDAP federation write path is unsupported because new accounts need numeric IDs. Ordinary OpenLDAP read-only LDAP federation is a different capability. | A cloud sign-in or an imported Authentik identity does not imply a corresponding writable NS8 domain account. | Provision users and groups through the authoritative NS8 directory workflow first and use read-only sync. Use the documented AD federation path only where it fits the deployment and directory write access is intended. |
| The reference module's exclusive federated realm mode requires exactly one enabled upstream IdP. It controls logins through that realm. Individual apps still need their own policy for local forms and password protocols. | Federated-only behavior can be inconsistent between the login page, desktop clients and non-browser protocols. | Keep mixed mode when multiple federated providers or an LDAP login are needed. In exclusive mode, use the app's documented recovery method and an independent administrator. Check each protocol before tightening access. |
| Webmail-to-Mail SSO needs the Mail audience and a valid access token for IMAP and SMTP. A successful webmail login only proves browser authentication. | Roundcube or WebTop can sign the user in but still fail to open the mailbox or send mail. Trust across application-specific issuers also requires an explicit Mail design. | Keep the app's supported password-based mail access until the provider, webmail and Mail server are tested together. Preserve issuer and audience checks and per-user mailbox authorization. |
| Multiple LDAP sources share Authentik's username namespace. In the reviewed version the LDAP password backend iterates enabled sources and uses the user's stored distinguished name. | Overlapping directory trees and duplicate usernames complicate identity ownership. Manual sources can be changed independently after NS8's validation. | Use disjoint naming contexts and distinct usernames, including manually managed sources. Complete a same-directory migration with one NS8 domain before adding more. Use directory identifiers with multiple NS8 domains and test that each pilot user reaches only its own account. |

The reference implementation's federation modes and LDAP account claims are recorded in its [README](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/README.md#federated-identity-providers). Authentik's mode-specific discovery paths and LDAP behavior are described in the [OAuth2/OIDC provider manual](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/#issuer-mode) and [LDAP backend source](https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/sources/ldap/auth.py).

### Check the application first

The NS8 rollout tracks each consuming app separately. Use these issues to find the intended behavior and verify what shipped in the version you run.

| Application | What to verify | Upstream tracking |
| --- | --- | --- |
| Nextcloud | Existing-user mapping, the expected LDAP identity claim, emergency direct login, and mobile, desktop and WebDAV access | [Nextcloud](https://github.com/NethServer/dev/issues/8262) |
| Roundcube | OIDC web login plus token-authenticated IMAP and SMTP. A compatible Mail module is a dependency. | [Roundcube](https://github.com/NethServer/dev/issues/8263) |
| Mail | Dovecot introspection or validation, token issuer and audience, per-user mailbox access, and existing password clients | [Mail](https://github.com/NethServer/dev/issues/8264) |
| NethVoice | Version-specific OIDC support, the existing SAML option, privileged account restrictions, and mobile clients | [NethVoice](https://github.com/NethServer/dev/issues/8265) |
| WebTop | Mail audience, refresh during long sessions, administrator recovery, and calendar and sync clients | [WebTop](https://github.com/NethServer/dev/issues/8266) |

## Playbook for manual Authentik OIDC

1. **Pick one app and a small pilot.** Keep a separate local administrator and verify its recovery login in a fresh browser session. Record the old provider, issuer, callback, account identifier, claim mappings, and group assignments. Take a restorable backup before moving an existing integration.
2. **Create a client for the app in Authentik.** In Authentik, create or link an Application and an OAuth2/OpenID Provider. Use the client type and flow the app documents. A server-side app normally uses a confidential client with the authorization code flow. Register the exact HTTPS callback reported by the app and any required exact logout return URL. Give the application appropriate access policies. Grant only the claims and scopes the app needs, typically `openid` and any required `profile`, `email` or application claims.
3. **Use the exact discovery values.** With Authentik's per-provider issuer mode, discovery is available from the application's slug path. Run this from a node or container that must reach Authentik, substituting your host and slug. The command reads public metadata only.

   ```sh
   curl -fsS 'https://auth.example.org/application/o/my-app/.well-known/openid-configuration' |
     jq '{issuer, authorization_endpoint, token_endpoint, userinfo_endpoint, jwks_uri, end_session_endpoint}'
   ```

   Copy the reported `issuer` exactly into the app, including any trailing slash. If the app asks for a discovery URL, enter the full URL in the example with your slug. Use a certificate trusted by the app container, and by the NS8 node when the node performs discovery. Validate issuer, signature, audience and normal OAuth/OIDC flow protections in the client. Keep secrets in the application's private settings or credential store.

4. **Choose the existing-account mapping before enabling public sign-in.** Preserve the existing Authentik app slug, client registration, signing settings and subject mode if other clients already rely on them. The application must recognize the pilot as the same account. An email link needs the application's verified ownership safeguards. Avoid automatic account or admin-role creation while checking mappings. Test one privileged user and at least one ordinary or restricted user.
5. **Exercise app-specific behavior.** In a fresh session verify sign-in, access to existing data, denied access where appropriate, logout and return URI, session refresh, and relevant mobile, desktop, mail or sync flows. Provider logout and application session termination can be separate actions.
6. **Rollback if needed.** Use the independent administrator and switch the app back to its saved sign-in method and mappings. Verify a fresh login into the original account. Once the cutover is verified, revoke unused clients in the provider and remove cached credentials following the application's procedure. If you changed LDAP source ownership as well, follow the [directory rollback guide](ns8-directory-login.md#roll-back-the-directory-switch).

### Examples from Genius Dynamics modules

These are configuration paths to look for in compatible versions. Confirm the labels and callback shown by your installed module.

- **Warpgate** offers **Advanced → Add external provider**. Register the HTTPS callback shown in Settings, normally `/@warpgate/api/sso/return` on the app host. Link existing Warpgate users to the specific provider in Warpgate. Keep local administrative access. [Warpgate module](https://github.com/geniusdynamics/ns8-warpgate#readme)
- **Termix** supports **Manual OIDC** when the SSO plugin is enabled. Module-managed SSO selects one provider. Use **Termix settings** if you need several UI-managed providers. New clients use the callback shown by Settings, normally `/plugin-api/sso/callback`. Existing registrations may retain an earlier callback. Start with password login enabled and silent redirect disabled. [Termix module](https://github.com/geniusdynamics/ns8-termix#readme)
- **Postal** offers manual OIDC and uses `/auth/oidc/callback` on the Postal host in the reviewed implementation. It uses one active provider and can link a pre-created account on first sign-in by email, clearing that account's local password. Keep a separate local administrator and resolve existing links before changing issuers. [Postal module](https://github.com/geniusdynamics/ns8-postal#readme)

### Troubleshooting by symptom

| Symptom | Check |
| --- | --- |
| Authentik never appears in the NS8 provider picker | Use the app's manual configuration for this module. Check the app version, domain binding and installed provider if you intended to use a supported native provider. |
| Discovery works in your browser but fails in the app | Check DNS, HTTPS routing, certificate trust, and access to the metadata and JWKS from the **app container**. For NS8-mediated discovery check the **node** as well. Ensure the configured issuer matches the discovery document and token issuer. |
| Callback or logout fails | Compare the request URI to the registered URI, including scheme, host, port, path, and any required trailing slash. Inspect the application's logs before changing provider settings. |
| User gets a blank account or wrong permissions | Pause the cutover. Compare the app's stored identity with the token issuer and subject or expected directory key. Review group claims and bindings before attempting another link. |
| LDAP connection is healthy but no users are imported | Check the sync job, worker health, LDAP search base and filters, and duplicate usernames. The web health check alone cannot prove the background worker is processing syncs. [Upgrade checks and logs](upgrades.md#verify-after-upgrading) |
| Webmail opens but the mailbox does not | Check that IMAP and SMTP are configured for the access token, the mail server trusts the issuer, and the Mail client is in the token audience. Use the supported password path while validating the complete integration. |

## What NS8 and the Authentik module need next

The following is a proposed compatibility contract for discussion with NS8 developers. It has no published compatibility guarantee. The scope of a first pilot is browser login for one consumer and one user domain.

| Area | Required addition |
| --- | --- |
| Discovery and negotiation | Add an explicit application-issuer mode that only capable consumers opt into. Keep the existing `oidc` realm contract available for existing apps. Define the provider identity, allowed public HTTPS origin, supported domain, capability flags, record version and change/withdrawal event. |
| Registration and authorization | Reuse the documented `register-client` behavior where possible. Grant the provider's specific role, for example `goauthentik@any:clientadm`, to upgraded clients. Derive the owner from trusted NS8 task context, confirm the caller's current domain binding, and preserve protections around administrator-only `module_id` overrides. Service discovery grants no registration permission. |
| Authentik resources | Reconcile a dedicated application and provider per registration, tagged with stable ownership such as caller module UUID and domain. Store the slug once. Scope access to users linked to the intended NS8 directory. Define least-privilege API credentials, secret storage and output retention, and a durable ownership record for backup and restore. |
| Reconciliation | Define idempotent retries, concurrent registration, lock ordering, secret rotation, administrative disabling and deletion on domain unbind or module removal. On startup reconcile after missed events. A temporarily unavailable node or service record is an availability failure and requires retry. An authoritative unbind or uninstall is a cleanup event. Preserve existing manually managed Authentik applications and sources. |
| Consumer changes | Authorize and discover the new provider type, register the client before deriving endpoints, and use the response's exact issuer. Validate the advertised HTTPS origin, reject issuers with credentials, a query, or a fragment, and compare the discovery issuer and token issuer exactly. When fetching metadata, join the discovery suffix with one slash and preserve the returned issuer for comparisons. Apply the normal signature, audience and flow protections. Persist provider UUID, domain and issuer. Treat a new issuer or identity key as an explicit migration. Keep previous working settings when refresh fails. |
| Identity and claims | Specify the mapping and casing of `preferred_username`, the stable subject and optional `ldap_uuid` behavior, group claims, account linking and deprovisioning. Test the values from real tokens. An LDAP connection or local username alone cannot establish claim parity. |
| Capabilities | Define machine-readable support or clear errors for additional audiences, introspection, CORS origins, and logout. A consumer must be able to tell when a provider cannot satisfy a requested capability. Defer mail/webmail integration until token audience, issuer and expiry are verified together. |
| Fleet behavior | Define how host and TLS changes, clone, restore, provider removal, and disabled accounts are handled. Test provider and consumer versions independently. Keep an explicit local recovery path and a way to revoke a client without affecting other apps. |

### Concrete compatibility proposal

One incremental option is a separate `srv/http/oidc-client` service and a corresponding `service-oidc-client-changed` event for providers with application-specific issuers. A capable consumer would look up that service for its domain, call `register-client`, then fetch the discovery document for the returned issuer. An existing consumer querying `srv/http/oidc` would continue to see the realm-based providers it supports. Exact service names, record layout for multiple domains, capability negotiation and event payloads need an upstream agreement.

For example, two clients in the same NS8 domain might receive `https://auth.example.org/application/o/ns8-cloud/` and `https://auth.example.org/application/o/ns8-webmail/`. These are distinct issuers on the advertised provider origin. Neither is derived from the directory name. A compatibility fixture exercised the existing NS8 discovery helper with simulated records and confirmed separation by service and domain. It did not exercise publication, authorization, client registration or sign-in with a real consumer.

Proxy path rewrites still have to satisfy the issuer in the discovery document and in signed tokens. Sharing a client across apps ties together their callbacks, credentials and revocation. Use the supported manual mode until a real consumer understands the application-specific contract. A separately administered OIDC broker can be an option where an operator already supports that topology. Treat federation behind a broker as its own integration and verify directory identity mapping, MFA policy, token audience and logout across both hops. The reference `ns8-idp` Entra workflow is not a general-purpose Authentik broker configuration. [Reference federation implementation](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/imageroot/pypkg/idpfed.py)

Two specific decisions are worth settling before writing the adapter:

- **Registration failures and rollback.** Keep the current validation errors for missing or unauthorized caller identity and unbound domains. Define an explicit result for unsupported capability, and decide how to clean up a newly created client when the consumer rejects the issuer or fails to apply its local configuration. Resolve ownership before deleting anything. Normal retries should neither rotate secrets nor create duplicate applications.
- **Credential handling.** The reviewed reference returns the client secret via NS8 task output, which is retained temporarily in Redis. Agree who can read it, how long it remains accessible, and whether Authentik can use that mechanism safely. Keep registration secrets out of UI responses, journal output, discovery records and diagnostics. Test consumer recovery after rotating a secret and after restoring a backup. [Reference credential handling](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/README.md#realms-and-clients)

### Acceptance checklist for a native pilot

- Run a legacy consumer with the reference realm-based provider, then install the candidate Authentik provider alongside it. The legacy picker and login path must continue working.
- Use an upgraded consumer to register two applications for one domain. Verify distinct clients and issuers, independent secrets, and stable issuer and subject values on repeated registration and rotation.
- Test one allowed user, a user from another source or domain, and a disabled user. Verify the original user account, group access, worker health and an independent recovery login.
- Verify an unauthorized module or unbound domain cannot register, update or remove the client. Re-register a disabled client and confirm it remains disabled.
- Test exact callback and logout URIs, expired and wrong-audience tokens, issuer mismatch, lost events, failed refresh, and removal or unbind. Confirm the app can recover without losing its previous valid configuration.
- Test fresh install and upgrade with manually configured providers and existing app account links. Check restart, backup and restore, and provider hostname changes.
- Keep browser-only pilot results separate from Mail, WebDAV, mobile and provisioning claims. Extend the matrix as those consumers become available.

## Keeping this guide current

For each future integration PR, record the core, reference provider, Authentik and consumer revisions tested. Recheck the developer manual, registration schema, release notes and issue statuses. Update the workarounds when a capability is implemented and verified on supported releases. A passing LDAP sync, a rendered settings page and a successful browser login are separate checks from native discovery and automatic registration.

- [NS8 SSO tracking issue](https://github.com/NethServer/dev/issues/8258) and [core contract at f0c4084](https://github.com/NethServer/ns8-core/blob/f0c4084473f2a75c0f226d77b413c872434bc61f/docs/core/user_domains.md#single-sign-on)
- [Reference `ns8-idp` at 4286689](https://github.com/NethServer/ns8-idp/tree/428668941469be93fc200c508718171f3c9cdd04) and its [registration schema](https://github.com/NethServer/ns8-idp/blob/428668941469be93fc200c508718171f3c9cdd04/imageroot/actions/register-client/validate-input.json)
- [Authentik 2026.8.5 issuer implementation](https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/providers/oauth2/models.py#L365) and [OIDC URL routes](https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/providers/oauth2/urls.py)
- [Multi-directory module change and QEMU evidence](https://github.com/geniusdynamics/ns8-goauthentik/pull/42)
