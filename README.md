# Authentik for NethServer 8

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Authentik Version](https://img.shields.io/badge/Authentik-2026.8.5-blue)](https://goauthentik.io/)

A comprehensive NethServer 8 module that integrates **Authentik**, the open-source Identity Provider, into your NethServer infrastructure. Authentik provides centralized authentication, authorization, and user management with support for OAuth2, SAML, LDAP, and many other protocols.

## ✨ Features

- **Centralized Identity Management**: Single sign-on (SSO) across all your applications
- **Multi-Protocol Support**: OAuth2, OpenID Connect, SAML, LDAP, SCIM, and more
- **User-Friendly Interface**: Modern Vue.js-based management interface
- **Enterprise-Ready**: Built for production environments with high availability
- **Extensible**: Support for custom flows, policies, and integrations
- **Secure**: Built-in security features including MFA, password policies, and audit logging

## 🚀 Quick Start

### Prerequisites

- NethServer 8 with core 3.23.0 or later
- Administrative access to the NethServer cluster
- A domain name for the Authentik instance

### Installation

1. **Add the module to your NethServer cluster:**

   ```bash
   add-module ghcr.io/geniusdynamics/goauthentik:latest 1
   ```

   The command will return output similar to:
   ```json
   {"module_id": "goauthentik1", "image_name": "goauthentik", "image_url": "ghcr.io/geniusdynamics/goauthentik:latest"}
   ```

2. **Configure the module:**

   ```bash
   api-cli run configure-module --agent module/goauthentik1 --data - <<EOF
   {
     "host": "auth.yourdomain.com",
     "http2https": true,
     "lets_encrypt": true
   }
   EOF
   ```

3. **Complete the initial setup:**

   - Open your browser and navigate to `https://auth.yourdomain.com/if/flow/initial-setup/`
   - Follow the on-screen instructions to complete the Authentik setup
   - Configure your first authentication flow and create administrative users

## ⚙️ Configuration

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `host` | string | Yes | Fully qualified domain name for the Authentik instance |
| `http2https` | boolean | Yes | Enable HTTP to HTTPS redirection |
| `lets_encrypt` | boolean | Yes | Enable Let's Encrypt SSL certificate |

### Example Configuration

```bash
api-cli run configure-module --agent module/goauthentik1 --data '{
  "host": "auth.company.com",
  "http2https": true,
  "lets_encrypt": true
}'
```

### Getting Current Configuration

```bash
api-cli run get-configuration --agent module/goauthentik1
```

## 🔧 Management Commands

### Update Module

To update to the latest version:

```bash
api-cli run update-module --data '{
  "module_url": "ghcr.io/geniusdynamics/goauthentik:latest",
  "instances": ["goauthentik1"],
  "force": true
}'
```

### Uninstall Module

To remove the Authentik instance:

```bash
remove-module --no-preserve goauthentik1
```

## 🏗️ Architecture

This module is built using modern containerized architecture:

- **Frontend**: Vue.js 2.x with Carbon Design System
- **Backend**: Authentik server with PostgreSQL and Redis
- **Containerization**: Podman with rootless containers
- **Reverse Proxy**: Traefik integration for SSL termination
- **Service Management**: Systemd user services

### Container Structure

- **Authentik Server**: Main application container
- **PostgreSQL**: Database backend
- **Redis**: Caching and session storage
- **Nginx**: Web server for static assets

## 🧪 Testing

The module includes comprehensive test suites using Robot Framework:

```bash
./test-module.sh <NODE_ADDR> ghcr.io/geniusdynamics/goauthentik:latest
```

Tests cover:
- Module installation and configuration
- Service availability and functionality
- Integration with NethServer core services
- SSL certificate management

## 🔍 Debugging

### Environment Variables

Check module environment variables:

```bash
runagent -m goauthentik1 env
```

### Container Inspection

List running containers:

```bash
runagent -m goauthentik1 podman ps
```

Access container shell:

```bash
runagent -m goauthentik1 podman exec -ti goauthentik-app sh
```

### Service Logs

View service logs:

```bash
runagent -m goauthentik1 journalctl --user -u goauthentik.service
```

## 🌐 Internationalization

The UI supports multiple languages and is translated using [Weblate](https://hosted.weblate.org/projects/ns8/):

- English (en)
- Spanish (es)
- Italian (it)
- German (de)
- Portuguese (pt, pt_BR)
- European Basque (eu)

### Adding Translations

1. Add the [GitHub Weblate app](https://docs.weblate.org/en/latest/admin/continuous.html#github-setup) to your repository
2. Add your repository to [hosted.weblate.org](https://hosted.weblate.org) or request addition to the ns8 Weblate project

## 🛠️ Development

### Project Structure

```
├── imageroot/              # Module configuration and scripts
│   ├── actions/           # Module actions (configure, install, etc.)
│   ├── systemd/           # Service definitions
│   └── events/            # Event handlers
├── ui/                    # Vue.js frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── dist/             # Built assets
├── tests/                # Robot Framework tests
├── build-images.sh       # Build script
└── README.md            # This file
```

### Building from Source

1. **Build the UI:**

   ```bash
   cd ui
   yarn install
   yarn build
   ```

2. **Build the container image:**

   ```bash
   ./build-images.sh
   ```

3. **Push to registry:**

   ```bash
   buildah push ghcr.io/geniusdynamics/goauthentik:latest
   ```

### Development Environment

Set up a development environment:

```bash
# Clone the repository
git clone https://github.com/geniusdynamics/ns8-goauthentik.git
cd ns8-goauthentik

# Install UI dependencies
cd ui
yarn install

# Start development server
yarn serve
```

## 📚 Documentation

- [Authentik Documentation](https://docs.goauthentik.io/)
- [NethServer 8 Documentation](https://nethserver.github.io/ns8-core/)
- [Community Forum Thread](https://community.nethserver.org/t/authentik-sso-app-for-nethserver-8/22873/105)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PRs

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Kemboi Elvis** - *Lead Developer* - [kemboielvis@genius.ke](mailto:kemboielvis@genius.ke)
- **Martin Bhuong** - *Contributor* - [martin@genius.ke](mailto:martin@genius.ke)

## 🙏 Acknowledgments

- [Authentik Project](https://goauthentik.io/) for the excellent identity management platform
- [NethServer Community](https://community.nethserver.org/) for the robust server platform
- [Genius Dynamics](https://genius.ke) for sponsoring this module development

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/geniusdynamics/ns8-goauthentik/issues)
- **Documentation**: [Authentik Docs](https://docs.goauthentik.io/)
- **Community**: [NethServer Community Forum](https://community.nethserver.org/)

---

**Made with ❤️ by the Genius Dynamics Team**

## Upgrade path

The compatibility release on Authentik 2025.12.6 accepts upgrades from
NS8 module 2.0.3 or later. Back up the module before switching versions.
For an existing 2025.8 installation, install module 2.0.3 (Authentik
2025.10.4) before moving to the 2025.12 line. Review duplicate group names
in Authentik before moving from 2025.10 to 2025.12. The preflight reports
duplicates without changing group or policy assignments.

The module persists new files under `/data` and mounts the existing media
volume under `/data/media`. The upgrade copies files from the previous
containers and keeps existing volume files if their names collide. The old
Redis data volume is retained on disk. Authentik uses PostgreSQL for its
cache and tasks.

Restore the pre-upgrade backup to go back to an earlier Authentik version.
Reinstalling the earlier image over a migrated database is unsupported.

### NS8 module 2.2.0

Upgrade from module 2.1.1 (Authentik 2025.12.6) to Authentik 2026.2.7.
The 2026.2 line deprecates `User.ak_groups` in custom expressions and property mappings. Review those expressions and switch to `User.groups`.

### NS8 module 2.3.0

Upgrade from module 2.2.0 (Authentik 2026.2.7) to Authentik 2026.5.8.
Keep this 2026.5.8 waypoint before 2026.8. The 2026.5.7 → 2026.8.2 route had an upstream migration-history regression.

### NS8 module 2.4.0

Upgrade from module 2.3.0 (Authentik 2026.5.8) to Authentik 2026.8.5.
The ingress remains bound to the module node loopback. Authentik trusts forwarded headers only from the loopback and the dedicated slirp4netns pod subnet.

## NS8 directory login

From **Settings**, select an NS8 user domain to provision a managed LDAP source
in Authentik. Active Directory and OpenLDAP domains use the node LDAP proxy,
with the filters and bind credentials for that domain. The deployment also
applies updated proxy settings after NS8 reports a domain change.

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
