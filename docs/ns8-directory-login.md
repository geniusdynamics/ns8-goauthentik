# NS8 directory login

For application sign-in and native NS8 OIDC compatibility, see the
[NS8 single sign-on guide](ns8-sso.md).

From **Settings**, select an NS8 user domain to provision a managed LDAP source
in Authentik. Active Directory and OpenLDAP domains use the node LDAP proxy,
with the filters and bind credentials for that domain. The deployment also
applies updated proxy settings after NS8 reports a domain change.

In the Authentik admin interface, open **Directory → Federation and Social login**.
Each selected domain appears as an LDAP source named **NS8 directory (your-domain)**.
Manage those sources from NS8 **Settings**. Administrators can still manage
independent LDAP sources in Authentik.

One user domain is enough to get started. Choose **Additional user domains**
to select more OpenLDAP or Active Directory domains already configured in NS8.
The module creates a separate managed LDAP source for each domain. Use
distinct usernames and LDAP naming contexts across directories. Authentik
has one username namespace, and a duplicate username can prevent an import.
The module checks for overlapping configured search bases when enabling
multiple domains, including enabled sources added in Authentik.

With multiple domains selected, imports match by directory identifier.
Existing links are retained. Username linking is available with one selected
domain for migrations where account ownership has been verified. Set up any
other LDAP connections directly in the Authentik interface. Removing a
selection disables its managed source and keeps its imported users and groups.

When moving an existing manual source for the same directory, migrate it with
one NS8 domain selected. After validating fresh app sign-ins with the old
source disabled, add further NS8 domains.

By default, users are matched by their directory identifiers. Choose
**Link by matching username** only for a migration from the same directory after
checking ownership of matching usernames in Authentik. The module keeps
its managed resources separate from manually configured LDAP sources and
gives synchronized groups distinct names. LDAP password writeback and
deletion of users missing from the directory are disabled.

Clearing the primary NS8 domain disables all NS8-managed sources and retains imported
identities. Locally administered login methods remain available independently.

### Migrate an existing Authentik setup to an NS8 directory

You can keep your current setup by leaving the NS8 user domain unselected.
If you switch, keep using your existing Authentik applications and providers.
Their issuer or SAML entity ID, client credentials, redirect URIs, and signing
keys should stay as they are. The change is how users sign in to Authentik.

| Current setup | Migration path |
| --- | --- |
| LDAP or Samba AD configured in Authentik and backed by the same directory as the NS8 domain | Verify that the NS8 directory maps each username to the same person. Use **Link by matching username** to attach the new source to existing Authentik users. Keep the old source available until you finish validation. |
| Local Authentik accounts | Keep a local administrator who is independent of LDAP and confirm that account can sign in. If you want existing users to move to LDAP, use **Link by matching username** only after verifying every overlapping username belongs to the same person. |
| A different directory, an external identity source, or uncertain username ownership | Keep the current sign-in path. Use **Use directory identifiers** for new, distinct users. Resolve username collisions or establish verified account links before moving existing users. Matching names or email addresses alone is insufficient evidence of ownership. |

#### Prepare and validate the switch

1. Take a restorable NS8 module backup. Verify local administrator access in a
   separate browser session. Record the current source configuration, group
   and policy bindings, and the attributes used for provisioning. For OIDC,
   record the subject mode and test-user `sub`. For SAML, record the NameID
   format and test-user value. Include any custom claims, group filters,
   authentication flows, and SCIM mappings that apps rely on.
2. For an existing LDAP source, compare the mappings before enabling the new
   one. For each username that overlaps, confirm ownership against the source
   directory, including privileged and service accounts. The first managed sync
   can process the whole selected domain. Rehearse on a staging instance if
   you need to check the effect before enabling it in production.
3. In NS8, open the Authentik module’s **Settings**, select the user domain,
   choose the matching mode, and save. In Authentik, check that the new source
   under **Directory → Federation and Social login** finishes syncing. Under
   **Synced Users**, verify that users being migrated are linked to their
   original Authentik accounts. If a username collision occurs, leave the old
   sign-in path in place and resolve the link before continuing. Creating a
   replacement user with the same name can change how applications identify
   the user.
4. Review application access before retiring the old source. The managed LDAP
   source syncs groups with distinct names and applies its own default user
   mappings. Confirm required group memberships, application and flow
   bindings, and emitted claims. Update policies or mappings where needed.
   Changes to username, email, groups, or other mapped attributes can affect
   a claim or NameID even when the Authentik account itself is preserved.
5. Use a new browser session to test fresh sign-in to each connected app
   with representative users, including an administrator and a user with
   restricted access. Confirm each app opens the existing account, identifiers
   and required claims still match, and access limits still apply. Include
   provisioning where enabled. Keep the original source available while
   checking mappings. In a controlled change window, disable the original
   source without deleting it, then repeat the checks so the old source
   cannot mask a failure in the new one.

#### Roll back the directory switch

To return to the old sign-in path, re-enable the original source in Authentik
if it was disabled. In the NS8 module settings, clear the selected user domain
and save. This disables the managed source and retains its imported identities.
Restore any application or flow bindings you changed, and verify a fresh
sign-in. Clearing the domain leaves account links, synchronized user profile
changes, and groups in place. Reapply the original mappings or restore the
pre-change backup if you need to reverse those changes. Keep the original
source until access to the connected apps is confirmed.
